import gymnasium
import prototwin
import asyncio
import nest_asyncio
import numpy as np

from typing import Any, List, Dict, Sequence, Optional, Type
from copy import deepcopy
from collections import OrderedDict

from stable_baselines3.common import env_util
from stable_baselines3.common.vec_env.util import copy_obs_dict, dict_to_obs, obs_space_info
from stable_baselines3.common.vec_env.base_vec_env import VecEnvStepReturn, VecEnvObs, VecEnvIndices, VecEnv as SbVecEnv

class Env(gymnasium.Env):
    def __init__(self, client: prototwin.Client) -> None:
        """
        Base Gymnasium environment for ProtoTwin Connect

        Args:
            client (prototwin.Client): The ProtoTwin Connect client.
        """
        self.client = client
        nest_asyncio.apply()
    
    def reset(self, *, seed: int|None = None, options: dict[str, Any]|None = None) -> tuple[Any, dict[str, Any]]:
        """
        Resets the environment to an initial internal state.

        Args:
            seed (int | None, optional): The random seed. Defaults to None.
            options (dict[str, Any] | None, optional): Additional information to specify how the environment is reset. Defaults to None.

        Returns:
            tuple[Any, dict[str, Any]]: Observation of the initial state and a dictionary containing auxiliary information.
        """
        result = super().reset(seed=seed, options=options)
        asyncio.run(self.client.reset())
        return result
    
    def get(self, address: int) -> bool|int|float:
        """
        Reads the value of a signal at the specified address.

        Args:
            address (int): The signal address.

        Returns:
            bool|int|float: The signal value.
        """
        return self.client.get(address)
    
    def set(self, address: int, value: bool|int|float) -> None:
        """
        Writes a value to a signal at the specified address.  

        Args:
            address (int): The signal address.
            value (bool | int | float): The value to write.
        """
        self.client.set(address, value)
    
    def step(self) -> None:
        """
        Steps the simulation forward in time by one time-step.
        """
        asyncio.run(self.client.step())

class VecEnvInstance(gymnasium.Env):
    def __init__(self, client: prototwin.Client, instance: int) -> None:
        """
        Base Vectorized Gymnasium environment for ProtoTwin Connect

        Args:
            client (prototwin.Client): The ProtoTwin Connect client.
            instance (int): The instance number.
        """
        self.client: prototwin.Client = client
        self.instance: int = instance # Instance number
        self.offset: int = 0 # Address offset from the first signal for the environment source to the first signal for the first environment instance
        self.stride: int = 0 # Number of addresses for each environment instance
        self.first: int = 0 # Address of the first signal for the environment source
        self.last: int = 0 # Address of the last signal for the environment source
        self.time: float = 0 # Time since reset for the environment instance

    def reset(self, *, seed: int|None = None, options: dict[str, Any]|None = None) -> tuple[Any, dict[str, Any]]:
        """
        Resets the environment instance to an initial internal state.

        Args:
            seed (int | None, optional): The seed that is used to initialize the environment's PRNG. Defaults to None.
            options (dict[str, Any] | None, optional): Additional information to specify how the environment instance is reset. Defaults to None.

        Returns:
            tuple[Any, dict[str, Any]]: Observation of the initial state and a dictionary containing auxiliary information.
        """
        result = super().reset(seed=seed, options=options)
        asyncio.run(self.client.reset_environment(self.instance))
        return result
    
    def apply(self, action: gymnasium.core.ActType) -> None:
        """
        Applies the specified actions in preparation for the next simulation step.

        Args:
            action (gymnasium.core.ActType): The actions to be applied.
        """
        pass

    def step(self):
        """
        Steps the environment forward in time by one time-step.
        """
        pass

    def get(self, address: int) -> bool|int|float:
        """
        Reads the value of a signal at the specified address.

        Args:
            address (int): The signal address.

        Returns:
            bool|int|float: The signal value.
        """
        if address >= self.first and address <= self.last:
            return self.client.get(address + self.offset + self.stride * self.instance)
        return self.client.get(address)
    
    def set(self, address: int, value: bool|int|float) -> None:
        """
        Writes a value to a signal at the specified address.  

        Args:
            address (int): The signal address.
            value (bool | int | float): The value to write.
        """
        if address >= self.first and address <= self.last:
            self.client.set(address + self.offset + self.stride * self.instance, value)
        else:
            self.client.set(address, value)

class VecEnv(SbVecEnv):
    actions: np.ndarray
    def __init__(self, env_type: Type[VecEnvInstance], client: prototwin.Client, entity_name: str, num_envs: int, observation_space: gymnasium.Space, action_space: gymnasium.Space, *, pattern: prototwin.Pattern = prototwin.Pattern.GRID, spacing: float = 1):
        """
        Vectorized Environment for ProtoTwin Connect.

        Args:
            env_type (Type[VecEnvInstance]): The vectorized environment instance type.
            client (prototwin.Client): The ProtoTwin Connect client.
            entity_name (str): The name of the entity that serves as the source for the environments.
            num_envs (int): The number of environment instances to create.
            observation_space (gymnasium.Space): The observation space for the environment instances.
            action_space (gymnasium.Space): The action space for the environment instances.
            pattern (prototwin.Pattern, optional): The pattern used to position the created environment instances. Defaults to prototwin.Pattern.GRID.
            spacing (float, optional): The spacing between environment instances. Defaults to 1.
        """
        nest_asyncio.apply()
        self.client = client
        self.envs: List[VecEnvInstance] = []
        self.reset_times: List[float] = []
        offset, stride, first, last = asyncio.run(client.create_environments(entity_name, num_envs, pattern=pattern, spacing=spacing))
        for i in range(num_envs):
            env = env_type(client, i)
            env.observation_space = observation_space
            env.action_space = action_space
            env.offset = offset
            env.stride = stride
            env.first = first
            env.last = last
            env.time = 0
            self.envs.append(env)
            self.reset_times.append(-1)

        super().__init__(num_envs, observation_space, action_space)
        self.keys, shapes, dtypes = obs_space_info(observation_space)

        self.buf_obs = OrderedDict([(k, np.zeros((self.num_envs, *tuple(shapes[k])), dtype=dtypes[k])) for k in self.keys])
        self.buf_dones = np.zeros((self.num_envs,), dtype=bool)
        self.buf_rews = np.zeros((self.num_envs,), dtype=np.float32)
        self.buf_infos: List[Dict[str, Any]] = [{} for _ in range(self.num_envs)]
        self.metadata = self.envs[0].metadata

    def step_async(self, actions: np.ndarray) -> None:
        """
        Tell all the environments to start taking a step
        with the given actions.
        Call step_wait() to get the results of the step.

        You should not call this if a step_async run is
        already pending.
        """
        self.actions = actions
        for _, (env, action) in enumerate(zip(self.envs, actions)):
            env.apply(action)

    def step_wait(self) -> VecEnvStepReturn:
        """
        Wait for the step taken with step_async().

        :return: observation, reward, done, information
        """
        asyncio.run(self.client.step())
        current_time = self.client.get(0)
        for env_idx in range(self.num_envs):
            env = self.envs[env_idx]
            if (env.time < 0):
                self.reset_times[env_idx] = current_time
            reset_time = self.reset_times[env_idx]
            env.time = current_time
            if reset_time >= 0:
                env.time -= reset_time
            obs, self.buf_rews[env_idx], terminated, truncated, self.buf_infos[env_idx] = env.step()
            self.buf_dones[env_idx] = terminated or truncated
            self.buf_infos[env_idx]["TimeLimit.truncated"] = truncated and not terminated
            if self.buf_dones[env_idx]:
                self.buf_infos[env_idx]["terminal_observation"] = obs
                obs, self.reset_infos[env_idx] = env.reset()
                env.time = -1
            self._save_obs(env_idx, obs)
        return (self._obs_from_buf(), np.copy(self.buf_rews), np.copy(self.buf_dones), deepcopy(self.buf_infos))

    def reset(self) -> VecEnvObs:
        """
        Reset all the environments and return an array of
        observations, or a tuple of observation arrays.

        If step_async is still doing work, that work will
        be cancelled and step_wait() should not be called
        until step_async() is invoked again.

        :return: observation
        """
        asyncio.run(self.client.initialize())
        for env_idx in range(self.num_envs):
            maybe_options = {"options": self._options[env_idx]} if self._options[env_idx] else {}
            env = self.envs[env_idx]
            obs, self.reset_infos[env_idx] = env.reset(seed=self._seeds[env_idx], **maybe_options)
            self._save_obs(env_idx, obs)
        self._reset_seeds()
        self._reset_options()
        return self._obs_from_buf()

    def close(self) -> None:
        """
        Clean up the environment's resources.
        """
        for env in self.envs:
            env.close()

    def get_images(self) -> Sequence[Optional[np.ndarray]]:
        """
        Return RGB images from each environment when available
        """
        return [None for _ in self.envs]

    def render(self, mode: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Gym environment rendering

        :param mode: the rendering type
        """
        return super().render(mode=mode)

    def _save_obs(self, env_idx: int, obs: VecEnvObs) -> None:
        for key in self.keys:
            if key is None:
                self.buf_obs[key][env_idx] = obs
            else:
                self.buf_obs[key][env_idx] = obs[key]

    def _obs_from_buf(self) -> VecEnvObs:
        return dict_to_obs(self.observation_space, copy_obs_dict(self.buf_obs))

    def get_attr(self, attr_name: str, indices: VecEnvIndices = None) -> List[Any]:
        target_envs = self._get_target_envs(indices)
        return [getattr(env_i, attr_name) for env_i in target_envs]

    def set_attr(self, attr_name: str, value: Any, indices: VecEnvIndices = None) -> None:
        target_envs = self._get_target_envs(indices)
        for env_i in target_envs:
            setattr(env_i, attr_name, value)

    def env_method(self, method_name: str, *method_args, indices: VecEnvIndices = None, **method_kwargs) -> List[Any]:
        target_envs = self._get_target_envs(indices)
        return [getattr(env_i, method_name)(*method_args, **method_kwargs) for env_i in target_envs]

    def env_is_wrapped(self, wrapper_class: Type[gymnasium.Wrapper], indices: VecEnvIndices = None) -> List[bool]:
        target_envs = self._get_target_envs(indices)
        return [env_util.is_wrapped(env_i, wrapper_class) for env_i in target_envs]

    def _get_target_envs(self, indices: VecEnvIndices) -> List[gymnasium.Env]:
        indices = self._get_indices(indices)
        return [self.envs[i] for i in indices]