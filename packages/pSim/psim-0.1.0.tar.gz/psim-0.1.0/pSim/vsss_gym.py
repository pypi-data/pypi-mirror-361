import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
import pygame
from gymnasium.wrappers import FlattenObservation

from pSim.modules.OUNoise import OrnsteinUhlenbeckNoise
from pSim.modules.curriculum_learning import CurriculumLearning
from pSim.modules.render_vsss import RenderVSSS
from pSim.modules.simulator import Simulator

sys.dont_write_bytecode = True

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.append(cwd)

M2P = 400


class VSSSEnv(gym.Env):
    """Custom Gymnasium Environment for Very Small Size Soccer (VSSS).

    This environment simulates a VSSS match, allowing AI agents to control
    robots and interact with a ball within a defined field.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(
        self,
        render_mode: Optional[str] = None,
        plan: Optional[int] = None,
        num_ally_robots: int = 1,
        num_enemy_robots: int = 0,
        single: bool = True,
        color_team: str = "blue",
    ):
        """Initializes the VSSSEnv environment.

        Args:
            render_mode: The rendering mode. Can be "human" for display or "rgb_array" for returning RGB images.
            plan: The curriculum learning plan to use.
            num_ally_robots: The number of ally robots in the simulation.
            num_enemy_robots: The number of enemy robots in the simulation.
            single: If True, only one ally robot is controlled by the agent.
            color_team: The color of the ally team ("blue" or "yellow").
        """
        super().__init__()
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window_size = np.asarray([1.70, 1.30]) * M2P

        self.window = None
        self.clock = None

        self.render_vsss = RenderVSSS()
        self.simulator = Simulator()
        self.cl = CurriculumLearning(plan, truncated_time=3600)

        self.num_ally_robots = num_ally_robots
        self.num_enemy_robots = num_enemy_robots

        self.color_team, self.color_enemy = (
            ("blue", "yellow") if color_team == "blue" else ("yellow", "blue")
        )
        self._init_positions()

        self.ou_noise_vw_enemy: List[Tuple[OrnsteinUhlenbeckNoise, OrnsteinUhlenbeckNoise]] = [
            (OrnsteinUhlenbeckNoise(), OrnsteinUhlenbeckNoise())
            for _ in range(num_enemy_robots)
        ]
        self.single = single
        self.ou_noise_vw_ally: List[Tuple[OrnsteinUhlenbeckNoise, OrnsteinUhlenbeckNoise]] = [
            (OrnsteinUhlenbeckNoise(), OrnsteinUhlenbeckNoise())
            for _ in range(num_ally_robots - 1)
            if single and num_ally_robots > 1
        ]

        self.action_robots = 1 if single else num_ally_robots
        num_features = 14 + 3 * (num_ally_robots - 1) + 3 * num_enemy_robots

        self.action_space = gym.spaces.Box(
            low=-1, high=1, shape=(self.action_robots, 2), dtype=np.float32
        )
        self.observation_space = gym.spaces.Tuple(
            tuple(
                gym.spaces.Box(
                    low=-np.inf, high=np.inf, shape=(num_features,), dtype=np.float32
                )
                for _ in range(self.action_robots)
            )
        )

    def _init_positions(self) -> None:
        """Initializes the positions of the ball and robots.

        This method uses the curriculum learning module to get the initial states
        for the ball and all robots (ally and enemy).
        """
        self.ball_pos, self.robots_pose = self.cl.get_states(
            self.simulator, self.num_ally_robots, self.num_enemy_robots
        )
        self.robots_ally, self.robots_enemy = (
            self.robots_pose[: self.num_ally_robots],
            self.robots_pose[self.num_ally_robots :],
        )

    def _get_obs(self) -> tuple:
        """Retrieves the current observation of the environment.

        Returns:
            A tuple containing the observations for each action robot.
        """
        observation = tuple(
            self.simulator.agent_observation(idx) for idx in range(self.action_robots)
        )
        return observation

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[tuple, Dict[Any, Any]]:
        """Resets the environment to an initial state.

        Args:
            seed: An optional seed for the random number generator.

        Returns:
            A tuple containing the initial observation and an info dictionary.
        """
        super().reset(seed=seed, options=options)

        self.simulator.world.ClearForces()
        self._init_positions()
        self.simulator.reset_simulator(
            self.robots_ally, self.ball_pos, self.robots_enemy
        )
        observation = self._get_obs()
        info = {}

        self.cl.t = 0

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action: np.ndarray) -> Tuple[tuple, float, bool, bool, Dict[Any, Any]]:
        """Performs one step in the environment using the given action.

        Args:
            action: The action to be taken by the agent(s).

        Returns:
            A tuple containing the observation, reward, terminated flag, truncated flag, and info dictionary.
        """
        for idx in range(self.num_ally_robots):
            if self.single and idx == 0:
                act = action[0]
                # act = action
            elif self.single and idx > 0:
                v, w = (
                    self.ou_noise_vw_ally[idx - 1][0].sample(),
                    self.ou_noise_vw_ally[idx - 1][1].sample(),
                )
                act = np.array([v, w])
            else:
                act = action[idx]
            self.simulator.agent_step(idx, act)

        for idx in range(self.num_enemy_robots):
            v, w = (
                self.ou_noise_vw_enemy[idx][0].sample(),
                self.ou_noise_vw_enemy[idx][1].sample(),
            )
            action = np.array([v, w])
            self.simulator.enemy_step(idx, action)

        self.simulator.world.Step(
            timeStep=1 / self.metadata["render_fps"],
            velocityIterations=6,
            positionIterations=2,
        )
        self.simulator.apply_force()

        observation = self._get_obs()
        self.cl.t += 1

        reward, terminated, truncated = self.cl.get_reward(self.simulator)

        info = {}

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self) -> Optional[np.ndarray]:
        """Renders the environment.

        Returns:
            An RGB array if render_mode is "rgb_array", otherwise None.
        """
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self) -> Optional[np.ndarray]:
        """Renders a single frame of the environment.

        This method handles the actual drawing operations using Pygame.
        """
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface(self.window_size)

        self.render_vsss.field(canvas)
        self.render_vsss.ball(
            canvas,
            self.simulator.ball_body.position.x,
            self.simulator.ball_body.position.y,
        )
        for idx in range(len(self.robots_ally)):
            self.render_vsss.robot(
                canvas,
                self.simulator.robots_ally[idx].position.x,
                self.simulator.robots_ally[idx].position.y,
                self.simulator.robots_ally[idx].angle,
                self.color_team,
                idx,
            )

        for idx in range(len(self.robots_enemy)):
            self.render_vsss.robot(
                canvas,
                self.simulator.robots_enemy[idx].position.x,
                self.simulator.robots_enemy[idx].position.y,
                self.simulator.robots_enemy[idx].angle,
                self.color_enemy,
                idx,
            )

        if self.render_mode == "human":
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
        else:
            return np.transpose(pygame.surfarray.array3d(canvas), axes=(1, 0, 2))

    def close(self):
        """Closes the Pygame window and quits Pygame."""
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()


def _main():
    """Main function to run the VSSS environment for demonstration.

    This function initializes the environment, runs a few episodes,
    and demonstrates the basic usage of the VSSSEnv class.
    """
    env = FlattenObservation(
        VSSSEnv(
            render_mode="human",
            plan=3,
            num_ally_robots=3,
            num_enemy_robots=3,
            single=False,
            color_team="yellow",
        )
    )
    obs, _, = env.reset()
    for _ in range(10):
        for _ in range(500):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                env.reset()
        env.reset()
    env.close()


if __name__ == "__main__":
    _main()
