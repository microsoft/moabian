from camera import OpenCVCameraSensor as Camera
from detector import HSVDetector as Detector
from hat import Hat


class MoabEnv:
    def __init__(self, hat=None, frequency=30, debug=False):
        if hat:
            # For cases like manual control where the hat needs to be shared
            self.hat = hat
        else:
            self.hat = Hat()
        self.camera = Camera(fps=frequency)
        self.detector = Detector()
        self.debug = debug

    def __enter__(self):
        self.hat.activate_plate()
        self.hat.hover_plate()
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.hat.lower_plate()
        self.hat.close()
        self.camera.stop()

    def reset(self, control_icon=None, control_name=None):
        if control_icon and control_name:
            self.hat.set_icon_text(control_icon, control_name)

    def step(self, action):
        plate_x, plate_y = action
        self.hat.set_plate_angles(plate_x, plate_y)

        frame, elapsed_time = self.camera(save=(self.debug == True))
        ball_detected, cicle_feature = self.detector(frame)

        return ball_detected, cicle_feature.center
