import time

from .camera import OpenCVCameraSensor as Camera
from .detector import HSVDetector as Detector
from .hat import Hat


class MoabEnv:
    def __init__(self, hat=None, frequency=25, debug=False):
        if hat:
            # For cases like manual control where the hat needs to be shared
            self.hat = hat
        else:
            self.hat = Hat()
        self.camera = Camera()
        self.detector = Detector()
        self.debug = debug

        self.dt = 1 / frequency
        self.prev_time = time.time()

    def __enter__(self):
        self.hat.activate_plate()
        self.hat.hover_plate()
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.hat.lower_plate()
        self.hat.disable_servo_power()
        self.hat.close()
        self.camera.stop()

    def reset(self, control_icon=None, control_name=None):
        if control_icon and control_name:
            self.hat.set_icon_text(control_icon, control_name)
        self.prev_time = time.time()
        # Return the state after a step with no motor actions
        return self.step((0, 0))

    def step(self, action):
        plate_x, plate_y = action
        self.hat.set_plate_angles(plate_x, plate_y)

        frame, elapsed_time = self.camera()
        ball_detected, cicle_feature = self.detector(frame, debug=self.debug)
        ball_center, ball_radius = cicle_feature

        # Wait until the next timestep to return state at the prev timestep
        # TODO: work out how we want to handle timing (delay by 1 timestep, have
        # asyncronous states/actions, etc)
        # Sleep until the next timestep
        time.sleep(max(self.prev_time + self.dt - time.time(), 0))
        self.prev_time = time.time()

        return ball_detected, ball_center
