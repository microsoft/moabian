import time

from camera import OpenCVCameraSensor as Camera
from detector import hsv_detector as detector
from common import high_pass_filter
from hat import Hat


class MoabEnv:
    def __init__(self, hat=None, frequency=30, debug=False):
        if hat:
            # For cases like manual control where the hat needs to be shared
            self.hat = hat
        else:
            self.hat = Hat()
        self.camera = Camera(frequency=frequency)
        self.detector = detector(debug=debug)
        self.debug = debug

        self.frequency = frequency
        self.dt = 1 / frequency
        self.prev_time = time.time()
        self.hpf_x, self.hpf_y = None, None
        self.sum_x, self.sum_y = 0, 0

    def __enter__(self):
        self.hat.enable_servos()
        self.hat.hover()
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.hat.lower()
        self.hat.disable_servos()
        self.hat.close()
        self.camera.stop()

    def reset(self, control_icon=None, control_name=None):
        if control_icon and control_name:
            self.hat.set_icon_text(control_icon, control_name)

        # Reset the derivative of the position
        # Use a high pass filter instead of a numerical derivative for stability.
        # A high pass filtered signal can be thought of as a derivative of a low
        # pass filtered signal: fc*s / (s + fc) = fc*s * 1 / (s + fc)
        # For more info: https://en.wikipedia.org/wiki/Differentiator
        # Or: https://www.youtube.com/user/ControlLectures/
        self.hpf_x = high_pass_filter(self.frequency, fc=15)
        self.hpf_y = high_pass_filter(self.frequency, fc=15)

        # Reset the integral of the position
        self.sum_x, self.sum_y = 0, 0

        # Return the state after a step with no motor actions
        return self.step((0, 0))

    def step(self, action):
        plate_x, plate_y = action
        self.hat.set_angles(plate_x, plate_y)

        frame, elapsed_time = self.camera()
        ball_detected, cicle_feature = self.detector(frame)
        ball_center, ball_radius = cicle_feature

        x, y = ball_center
        # Update derivate calulation
        vel_x, vel_y = self.hpf_x(x), self.hpf_y(y)
        # Update the summation (integral calculation)
        self.sum_x += x
        self.sum_y += y

        ## TODO: Test on more bots whether this sleep is necessary since camera
        ##       is a blocking call that does the timing too
        ## Wait until the next timestep to return state at the prev timestep
        # if self.prev_time + self.dt - time.time() < 0:
        #    print("Missed frame")
        ## Sleep until the next timestep
        # time.sleep(max(self.prev_time + self.dt - time.time(), 0))
        # self.prev_time = time.time()

        return ball_detected, (x, y, vel_x, vel_y, self.sum_x, self.sum_y)
