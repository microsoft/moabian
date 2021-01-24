import time

from env.hat import Hat, Icon, Text
from env.env import MoabEnv
from env.common import Vector2


class ManualController:
    def __init__(self, hat, max_angle=22):
        self.hat = hat
        self.max_angle = max_angle

    def __call__(self, state):
        menu_btn, joy_btn, joy_x, joy_y = self.hat.poll_buttons()
        action = Vector2(-joy_y, joy_x)
        return action * self.max_angle


def main():
    # Only manual needs access to the hat outside of the env
    hat = Hat()
    with MoabEnv(hat=hat, frequency=22, debug=True) as env:
        controller = ManualController(hat)
        state = env.reset(Icon.DOT, Text.MANUAL)
        while True:
            action = controller(state)
            print(action)
            env.step(action)


if __name__ == "__main__":
    main()
