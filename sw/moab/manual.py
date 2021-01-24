import time

from hat import Hat
from env import MoabEnv
from common import Vector2


class ManualController:
    def __init__(self, hat, max_angle=22):
        self.hat = hat
        self.max_angle = max_angle

    def __call__(self, state):
        menu_btn, joy_btn, joy_x, joy_y = self.hat.poll_buttons()
        action = Vector2(-joy_y, joy_x)
        return action * self.max_angle


def main():
    hat = Hat()
    frequency = 30
    with MoabEnv(hat=hat, frequency=frequency) as env:
        controller = ManualController(hat)
        env.step((0, 0))
        while True:
            action = controller()
            print(action)
            env.step(action)
            time.sleep(1.0 / frequency)


if __name__ == "__main__":
    main()
