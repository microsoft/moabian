# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Brain Controller

Connect to a locally running brain server and
ask for plate angles based on current hardware state.
"""

import math
import time
import requests
import numpy as np
import logging as log

from typing import Dict
from dataclasses import dataclass
from control.hat import interface as hat

from ..common import CircleFeature, IController, IDevice, Vector2


# Some type aliases for clarity
Plane = np.ndarray
Ray = np.ndarray


# Helper functions for linear algebra
def rotation_about_x(theta):
    return np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), np.sin(theta)],
            [0, -np.sin(theta), np.cos(theta)],
        ]
    )


def rotation_about_y(theta):
    return np.array(
        [
            [np.cos(theta), 0, -np.sin(theta)],
            [0, 1, 0],
            [np.sin(theta), 0, np.cos(theta)],
        ]
    )


class BrainController(IController):
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.

    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.
    """

    @dataclass
    class Config(IController.Config):
        endPoint: str = "localhost:5000"
        sensorSize: int = 256

    def __init__(self, config: Config, device: IDevice):
        super().__init__(config, device)
        self.config = config

        self.max_angle = self.config.maxAngle
        self.default_endpoint = self.config.endPoint
        self.prediction_url = f"{self.default_endpoint}/v1/prediction"

        self.velocity = Vector2(0, 0)
        self.prev_position = Vector2(0, 0)
        self.currPlateAngles = Vector2(0, 0)

    def _surface_plane(self) -> Plane:
        """
        Create a plane represent the surface of the plate
        in meters.
        """
        plate_theta_x = math.radians(self.currPlateAngles.x)
        plate_theta_y = math.radians(self.currPlateAngles.y)

        # get the plate normal
        x_rot = rotation_about_x(plate_theta_x)
        y_rot = rotation_about_y(plate_theta_y)

        # pitch then roll
        v = np.array([0.0, 0.0, 1.0]) @ x_rot @ y_rot
        plate_normal = v / np.linalg.norm(v)

        # create the plane
        PLATE_ORIGIN_Z = 0.020  # full range is 40mm of z-travel
        PLATE_ORIGIN_TO_SURFACE_OFFSET = 0.009  # 9mm above origin
        plate_surface = np.array(
            [0.0, 0.0, PLATE_ORIGIN_Z + PLATE_ORIGIN_TO_SURFACE_OFFSET]
        )
        return np.array([*plate_normal, np.sum(plate_normal * plate_surface)])

    def _detector_to_controller_units(self, pixels: CircleFeature) -> CircleFeature:
        """
        Convert a set of coordinates in pixels to meters

        The input is a 2D point in sensor image space.
        To get the location in meters, we need to unproject the camera
        back to the plate surface plane.

        We can derive the plate surface plane from the plate
        angles and distances.
        """
        # The plate is roughly 85% of the field of view
        PLATE_DIA_METERS = 0.225
        PLATE_DIA_PIXELS = self.config.sensorSize * 0.85
        scalar = PLATE_DIA_METERS / PLATE_DIA_PIXELS

        # basic linear transform
        meters = CircleFeature(
            Vector2(pixels.center.x * scalar, pixels.center.y * scalar),
            pixels.radius * scalar,
        )
        return meters

    @staticmethod
    def heading_to_point(start: Vector2, vel: Vector2, point: Vector2):
        """
        Return a heading, in 2D RH coordinate system.
        start:  the current position of the object
        vel:    the current velocity vector of motion for the object
        point:  the destination point to head towards

        returns: offset angle in radians in the range [-pi .. pi]
        where:
            0.0:                object is moving directly towards the point
            [-pi .. <0]:   object is moving to the "right" of the point
            [>0 .. -pi]:   object is moving to the "left" of the point
            [-pi, pi]: object is moving directly away from the point
        """
        # vectors and lengths
        u = (point - start).normalized()
        v = vel.normalized()

        # no velocity? already on the target?
        angle = 0.0
        if (u.length() != 0.0) and (v.length() != 0.0):
            # signed angle
            cr = Vector2(-u.y, u.x)
            angle = math.atan2(cr.dot(v), u.dot(v))
            if math.isnan(angle):
                angle = 0.0
        return angle

    def _actions_for_state(
        self, elapsedSec: float, ball: CircleFeature, obstacle: CircleFeature
    ) -> Vector2:
        if elapsedSec > 0.0:
            self.velocity = (ball.center - self.prev_position) / elapsedSec

        obstacle_direction = BrainController.heading_to_point(
            ball.center, self.velocity, obstacle.center
        )
        obstacle_distance = obstacle.center.distance(ball.center) - (
            ball.radius + obstacle.radius
        )

        observables = {
            # BonsaiMoabSimV4
            "elapsed_time": elapsedSec,
            "plate_theta_x": math.radians(self.currPlateAngles.x),
            "plate_theta_y": math.radians(self.currPlateAngles.y),
            "ball_x": ball.center.x,
            "ball_y": ball.center.y,
            "ball_radius": ball.radius,
            "ball_vel_x": self.velocity.x,
            "ball_vel_y": self.velocity.y,
            "obstacle_x": obstacle.center.x,
            "obstacle_y": obstacle.center.y,
            "obstacle_radius": obstacle.radius,
            "obstacle_distance": obstacle_distance,
            "obstacle_direction": obstacle_direction,
            # BonsaiMoabSimV3 legacy names. delete soon
            "obstacle_pos_x": obstacle.center.x,
            "obstacle_pos_y": obstacle.center.y,
            "distance_to_obstacle": obstacle_distance,
            "direction_to_obstacle": obstacle_direction,
        }

        log.debug(
            f"b:{ball.center} r: {ball.radius:2.3f}, o:{obstacle.center} r: {obstacle.radius:2.3f} "
            f"do:{obstacle_distance:2.3f} hd:{math.degrees(obstacle_direction):2.1f}"
        )

        # Trap on GET failures so we can restart the brain without
        # bringing down this run loop. Plate will default to level
        # when it loses the connection.
        result = Vector2(0, 0)
        try:
            action = requests.get(self.prediction_url, json=observables).json()

            for key, _ in action.items():
                action[key] *= self.max_angle
                action[key] = np.clip(action[key], -self.max_angle, self.max_angle)

            self.prev_position = ball.center
            result = Vector2(action["input_pitch"], action["input_roll"])
        except Exception as e:
            log.exception(f"Exception calling predictor\n{e}")
            pass

        return result

    def on_menu_down(self, sender: IDevice):
        sender.stop()

        # Hover the plate and deactivate the servos
        hat.hover_plate()
        time.sleep(0.5)
        hat.disable_servo_power()
        time.sleep(0.5)

    def getControlOutput(
        self,
        sender: IDevice,
        elapsedSec: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:
        # Calculate plate position using controller-specific factors
        self.currPlateAngles = currPlateAngles

        ball_real = CircleFeature(Vector2(0, 0), 0.0)
        detected = detectorResults.get("ball")
        if detected is not None:
            ball = CircleFeature(detected.center, detected.radius)
            ball_real = self._detector_to_controller_units(ball)

        # Unpack and convert the obstacle if present
        obstacle_real = CircleFeature(Vector2(0, 0.03), 0.020)
        detected = detectorResults.get("obstacle")
        if detected is not None:
            obstacle = CircleFeature(detected.center, detected.radius)
            obstacle_real = self._detector_to_controller_units(obstacle)

        plate_angles = self._actions_for_state(elapsedSec, ball_real, obstacle_real)
        return plate_angles
