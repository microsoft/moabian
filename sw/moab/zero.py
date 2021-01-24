import time

from hw.hat import Hat, Icon, Text
from hw.env import MoabEnv
from hw.common import Vector2


class ZeroController:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, state):
        return Vector2(0, 0)


def main():
    with MoabEnv(debug=True) as env:
        controller = ZeroController(0)
        state = env.reset(Icon.DOT, Text.BLANK)
        while True:
            action = controller(state)
            print(action)
            env.step(action)


if __name__ == "__main__":
    main()
