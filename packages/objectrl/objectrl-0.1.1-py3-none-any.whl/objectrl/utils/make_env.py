# -----------------------------------------------------------------------------------
# ObjectRL: An Object-Oriented Reinforcement Learning Codebase 
# Copyright (C) 2025 ADIN Lab

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------------

import gymnasium as gym
import numpy as np
import torch
from gymnasium.wrappers import RescaleAction

from objectrl.utils.environment.noisy_wrappers import (
    NoisyActionWrapper,
    NoisyObservationWrapper,
)
from objectrl.utils.environment.reward_wrappers import PositionDelayWrapper


def make_env(env_name: str, seed: int, env_config, eval_env=False) -> gym.Env:
    """
    Create and configure a Gymnasium environment with optional wrappers for noise,
    reward shaping, and consistent seeding.

    This function supports:
    - Action rescaling to [-1, 1]
    - Noisy action and/or observation wrappers
    - Delayed reward and control cost penalties via PositionDelayWrapper
    - Reproducibility via consistent seeding for Gym, NumPy, and PyTorch

    Args:
        env_name (str): Name of the Gym environment (must be registered in Gym).
        seed (int): Base random seed for reproducibility.
        env_config: Configuration object with nested attributes:
            - env_config.noisy.noisy_act (float): Std of Gaussian noise for actions.
            - env_config.noisy.noisy_obs (float): Std of Gaussian noise for observations.
            - env_config.position_delay (int): Delay threshold for reward.
            - env_config.control_cost_weight (float): Weight for control cost in reward.
        eval_env (bool, optional): If True, modifies seed to separate training/testing. Defaults to False.

    Returns:
        gym.Env: The fully constructed and wrapped Gymnasium environment instance.

    Raises:
        gym.error.Error: If `env_name` is not registered in Gym.
    """
    seed = seed + (100 if eval_env else 0)
    # Check if the env is in gym.
    env_ids = list(gym.envs.registry.keys())

    if env_name in env_ids:
        env = gym.make(env_name)

    if not isinstance(env.action_space, gym.spaces.Discrete):
        env = RescaleAction(env, np.float32(-1.0), np.float32(1.0))

    if env_config.noisy:
        if env_config.noisy.noisy_act > 0:
            env = NoisyActionWrapper(env, noise_act=env_config.noisy.noisy_act)
        if env_config.noisy.noisy_obs > 0:
            env = NoisyObservationWrapper(env, noise_obs=env_config.noisy.noisy_obs)

    if env_config.position_delay or env_config.control_cost_weight:
        env = PositionDelayWrapper(
            env,
            position_delay=env_config.position_delay,
            ctrl_w=env_config.control_cost_weight,
        )

    env.reset(seed=seed)
    env.action_space.seed(seed)
    env.observation_space.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    return env
