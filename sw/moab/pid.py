import time
import numpy as np

from hw.hat import Icon, Text
from hw.env import MoabEnv
from hw.common import Vector2


class HighPassFilter:
    def __init__(self, frequency, fc=50):
        self.x_dot_cstate = 0
        self.frequency = frequency
        self.fc = fc

    def reset(self):
        self.x_dot_cstate = 0

    def __call__(self, x):
        x_dot = -(self.fc ** 2) * self.x_dot_cstate + self.fc * x
        self.x_dot_cstate += (-self.fc * self.x_dot_cstate + x) / self.frequency
        return x_dot


class PIDController:
    def __init__(
        self,
        Kp=0.15 / 2.375,  # Proportional coefficient
        Ki=0.001 / 2.375,  # Integral coefficient
        Kd=0.090 / 2.375,  # Derivative coefficient
        fc=15,  # Cutoff frequency of the high pass filter
        frequency=25,
    ):
        # TODO: The PID controller should probably use matrices instead of 2
        #       independent SISO (single-input single-output) controls.
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.fc = fc
        self.frequency = frequency

        # Use a high pass filter instead of a numerical derivative for stability.
        # A high pass filtered signal can be thought of as a derivative of a low
        # pass filtered signal: fc*s / (s + fc) = fc*s * 1 / (s + fc)
        # For more info: https://en.wikipedia.org/wiki/Differentiator
        # Or: https://www.youtube.com/user/ControlLectures/
        self.hpf_x = HighPassFilter(self.frequency, self.fc)
        self.hpf_y = HighPassFilter(self.frequency, self.fc)

        self.sum_x = 0
        self.sum_y = 0

    def __call__(self, state):
        ball_detected, position = state
        x, y = position
        if ball_detected:
            action_x = self.Kp * x + self.Ki * self.sum_x + self.Kd * self.hpf_x(x)
            action_y = self.Kp * y + self.Ki * self.sum_y + self.Kd * self.hpf_y(y)
            # action_x = np.clip(action_x, -22, 22)
            # action_y = np.clip(action_y, -22, 22)
            action = Vector2(action_x, -action_y)
            # Update the integral term
            self.sum_x += x
            self.sum_y += y
            # print("Ball found")
        else:
            # Move plate back to flat
            action = Vector2(0, 0)
            # print("No ball")

        return action


def main():
    with MoabEnv() as env:
        controller = PIDController()
        state = env.reset(Icon.DOT, Text.CLASSIC)
        while True:
            action = controller(state)
            env.step(action)


if __name__ == "__main__":
    main()
