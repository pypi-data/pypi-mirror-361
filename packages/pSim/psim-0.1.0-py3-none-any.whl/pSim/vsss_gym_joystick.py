import os
import sys

import numpy as np
import pygame
from gymnasium.wrappers import FlattenObservation
from pygame.locals import JOYAXISMOTION, JOYBUTTONDOWN, JOYDEVICEADDED, JOYDEVICEREMOVED

from pSim.vsss_gym import VSSSEnv

sys.dont_write_bytecode = True

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.append(cwd)


class Joystick:
    def __init__(self, env):
        self.env = env
        self.env.reset()

        pygame.init()

        pygame.joystick.init()
        self.joysticks = self.update_joystick_list()
        self.active = True
        self.axes = {"LV": 1, "RH": 3}
        self.V = 0
        self.W = 0

    def update_joystick_list(self, verbose=False):
        joysticks = [
            pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
        ]
        for joystick in joysticks:
            joystick.init()
        if verbose:
            for joystick in joysticks:
                print(joystick.get_name())
        return joysticks

    def stop(self):
        self.active = False

    def loop(self):
        while self.active:
            for event in pygame.event.get():
                if event.type == JOYDEVICEADDED:
                    self.joysticks = self.update_joystick_list()
                if event.type == JOYDEVICEREMOVED:
                    self.joysticks = self.update_joystick_list()

                if event.type == JOYBUTTONDOWN:
                    if event.button == 1:
                        self.stop()
                    if event.button == 6:
                        self.env.reset()

                if event.type == JOYAXISMOTION:
                    if event.axis == self.axes["LV"]:
                        self.V = -event.value
                    if event.axis == self.axes["RH"]:
                        self.W = -event.value

            action = np.array([[self.V, self.W]])
            observation, reward, terminated, truncated, info = self.env.step(action)
            if terminated or truncated:
                self.env.reset()
        pygame.quit()


def main():
    env = FlattenObservation(
        VSSSEnv(
            render_mode="human",
            plan=1,
            num_ally_robots=1,
            num_enemy_robots=0,
            single=True,
            color_team="blue",
        )
    )
    joystick = Joystick(env=env)
    joystick.loop()
    env.close()


if __name__ == "__main__":
    main()
