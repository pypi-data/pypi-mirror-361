from .vsss_gym import VSSSEnv
from gymnasium.envs.registration import register

register(
    id="VSSS/Env-v0",
    entry_point="pSim.vsss_gym:VSSSEnv",
    max_episode_steps=3600,
)
