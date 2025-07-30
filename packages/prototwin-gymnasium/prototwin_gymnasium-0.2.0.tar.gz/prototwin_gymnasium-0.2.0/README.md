# ProtoTwin Gymnasium Environment

This package provides a base environment for [Gymnasium](https://gymnasium.farama.org/index.html), to be used for reinforcement learning.

## Introduction

ProtoTwin Connect allows external applications to issue commands for loading models, stepping the simulation and reading/writing signals. This package provides a base environment for Gymnasium, a library for reinforcement learning. ProtoTwin Connect is a drop-in replacement for existing physics libraries like PyBullet and MuJoCo. The advantage provided by ProtoTwin Connect is that you don't need to programatically create your robot/machine or start with an existing URDF file. Instead, you can import your CAD into ProtoTwin and, with a few clicks of the mouse, define rigid bodies, collision geometry, friction materials, joints and motors.

### Signals

Signals represent I/O for components defined in ProtoTwin. The [prototwin package](https://pypi.org/project/prototwin/) provides a client for starting and connecting to an instance of ProtoTwin Connect. Using this client you can issue commands to load a model, step the simulation forwards in time, read signal values and write signal values. Some examples of signals include:

* The current simulation time
* The target position for a motor
* The current velocity of motor
* The current force/torque applied by a motor
* The state of a volumetric sensor (blocked/cleared)
* The distance measured by a distance sensor
* The accelerations measured by an accelerometer

Signals are either readable or writable. For example, the current simulation time is readable whilst the target position for a motor is writable. Writable signals can also be read, but readable signals cannot be written.

#### Types

Signals are strongly typed. The following value types are supported:

* Boolean
* Uint8
* Uint16
* Uint32
* Int8
* Int16
* Int32
* Float
* Double

You can find the signals provided by each component inside ProtoTwin under the I/O dropdown menu. The I/O window lists the name, address and type of each signal along with its access (readable/writable). Python does not natively support small integral types. The client will automatically clamp values to the range of the integral type. For example, attempting to set a signal of type Uint8 to the value 1000 will cause the value to be clamped at 255.

#### Custom Signals

Many of the components built into ProtoTwin provide their own set of signals. However, it is also possible to create your own components with their own set of signals. This is done my creating a scripted component inside of ProtoTwin and assigning that component to one or more entities. The example below demonstrates a simple custom component that generates a sinusoidal wave and provides a readable signal for the amplitude of the wave. The value of this signal can be read at runtime through the ProtoTwin Connect python client.

```
import { Component, type Entity, DoubleSignal, Access, IO, Units, UnitType } from "prototwin";

export class SineWaveGeneratorIO extends IO {
    public frequency: DoubleSignal;
    public amplitude: DoubleSignal;

    public constructor() {
        super();
        this.frequency = new DoubleSignal(1, Access.Writable); // Input (writable)
        this.amplitude = new DoubleSignal(0, Access.Readable); // Output (readable)
    }
}

export class SineWaveGenerator extends Component {
    #io: SineWaveGeneratorIO;
    
    public override get io(): SineWaveGeneratorIO {
        return this.#io;
    }

    public override set io(value: SineWaveGeneratorIO) {
        this.#io = value;
    }

    @Units(UnitType.Frequency)
    public get frequency(): number {
        return this.#io.frequency.value;
    }

    public set frequency(value: number) {
        this.#io.frequency.value = value;
    }

    constructor(entity: Entity) {
        super(entity);
        this.#io = new SineWaveGeneratorIO();
    }

    public override update(dt: number) {
        this.#io.amplitude.value = Math.sin(2 * Math.PI * this.frequency * this.entity.world.time);
    }
}
```

## Example

This example demonstrates training an [inverted pendulum to swing up and balance](https://www.youtube.com/watch?v=W9wx2ZqYVJA).
Note that this example requires [ProtoTwin Connect](https://prototwin.com) to be installed on your local machine.

### Non-Vectorized

```
# STEP 1: Import dependencies
import prototwin_gymnasium
import prototwin
import asyncio
import os
import math
import time
import keyboard
import numpy as np
import torch as th
from typing import Tuple
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.policies import BasePolicy
from stable_baselines3.common.callbacks import CheckpointCallback

# STEP 2: Define signal addresses (obtain these values from ProtoTwin)
address_time = 0
address_cart_target_velocity = 3
address_cart_position = 5
address_cart_velocity = 6
address_cart_force = 7
address_pole_angle = 12
address_pole_angular_velocity = 13

# STEP 3: Create your environment by extending the base environment
class CartPoleEnv(prototwin_gymnasium.Env):
    def __init__(self, client: prototwin.Client) -> None:
        super().__init__(client)
        self.x_threshold = 0.65 # Maximum cart distance

        # The action space contains only the cart's target velocity
        action_high = np.array([1.0], dtype=np.float32)
        self.action_space = spaces.Box(-action_high, action_high, dtype=np.float32)

        # The observation space contains:
        # 0. A measure of the cart's distance from the center, where 0 is at the center and +/-1 is at the limit.
        # 1. A measure of the angular distance of the pole from the upright position, where 0 is at the upright position and 1 is at the down position.
        # 2. The cart's current velocity (m/s).
        # 3. The pole's angular velocity (rad/s).
        observation_high = np.array([1, 1, np.finfo(np.float32).max, np.finfo(np.float32).max], dtype=np.float32)
        self.observation_space = spaces.Box(-observation_high, observation_high, dtype=np.float32)

    def reward(self, obs):
        distance = 1 - math.fabs(obs[0]) # How close the cart is to the center
        angle = 1 - math.fabs(obs[1]) # How close the pole is to the upright position
        force = math.fabs(self.get(address_cart_force)) # How much force is being applied to drive the cart's motor
        return (angle * angle) * 0.8 + (distance * distance) * 0.2 - force * 0.001

    def reset(self, seed = None):
        super().reset(seed=seed)
        return np.array([0, 0])

    def step(self, action):
        self.set(address_cart_target_velocity, action) # Apply action by setting the cart's target velocity
        super().step() # Step the simulation forwards by one time-step
        time = self.get(address_time) # Read the current simulation time
        cart_position = self.get(address_cart_position) # Read the current cart position
        cart_velocity = self.get(address_cart_velocity) # Read the current cart velocity
        pole_angle = self.get(address_pole_angle) # Read the current pole angle
        pole_angular_velocity = self.get(address_pole_angular_velocity) # Read the current pole angular velocity
        pole_angular_distance = math.atan2(math.sin(math.pi - pole_angle), math.cos(math.pi - pole_angle)) # Calculate angular distance from upright position
        obs = np.array([cart_position / self.x_threshold, pole_angular_distance / math.pi, cart_velocity, pole_angular_velocity]) # Set observation space
        reward = self.reward(obs) # Calculate reward
        done = abs(obs[0]) > 1 # Terminate if cart goes beyond limits
        truncated = time > 20 # Truncate after 20 seconds
        return obs, reward, done, truncated, {}

# STEP 4: Setup the training session
async def train():
    # Start ProtoTwin Connect
    client = await prototwin.start()

    # Load the ProtoTwin model
    filepath = os.path.join(os.path.dirname(__file__), "CartPole.ptm")
    await client.load(filepath)

    # Create the environment
    env = CartPoleEnv(client)

    # Define the ML model
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./tensorboard/")

    # Create callback to regularly save the model
    checkpoint_callback = CheckpointCallback(save_freq=save_freq, save_path="./logs/checkpoints/", name_prefix="checkpoint", save_replay_buffer=True, save_vecnormalize=True)

    # Start learning!
    model.learn(total_timesteps=2_000_000, callback=checkpoint_callback)

# STEP 5: Setup the evaluation session
async def evaluate():
    # Start ProtoTwin Connect
    client = await prototwin.start()

    # Load the ProtoTwin model
    filepath = os.path.join(os.path.dirname(__file__), "CartPole.ptm")
    await client.load(filepath)
    
    # Create the environment
    env = CartPoleEnv(client)

    # Load the trained ML model
    model = PPO.load("logs/best_model/best_model", env)

    # Run simulation at real-time speed
    while True:
        env.reset()
        done = False
        obs = [0, 0, 0, 0]
        start_wall_time = time.perf_counter()
        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, truncated, info = env.step(action)
            if keyboard.is_pressed("r"):
                break
            current_wall_time = time.perf_counter()
            elapsed_wall_time = current_wall_time - start_wall_time
            elapsed_sim_time = client.get(address_time)
            sleep_time = elapsed_sim_time - elapsed_wall_time
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

asyncio.run(train())
```

### Vectorized

```
# STEP 1: Import dependencies
import asyncio
import stable_baselines3.ppo
import stable_baselines3.ppo.ppo
import torch
import os
import gymnasium
import numpy as np
import math
import prototwin
import stable_baselines3
import stable_baselines3.common
import stable_baselines3.common.vec_env
import stable_baselines3.common.vec_env.base_vec_env
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecMonitor
from stable_baselines3.common.callbacks import CheckpointCallback
from prototwin_gymnasium import VecEnvInstance, VecEnv

# STEP 2: Define signal addresses (obtain these values from ProtoTwin)
address_time = 0
address_cart_target_velocity = 3
address_cart_position = 5
address_cart_velocity = 6
address_cart_force = 7
address_pole_angle = 12
address_pole_angular_velocity = 13

# STEP 3: Create your vectorized instance environment by extending the base environment
class CartPoleEnv(VecEnvInstance):
    def __init__(self, client: prototwin.Client, instance: int) -> None:
        super().__init__(client, instance)
        self.x_threshold = 0.65 # Maximum cart distance

        # The action space contains only the cart's target velocity
        action_high = np.array([1.0], dtype=np.float32)
        self.action_space = gymnasium.spaces.Box(-action_high, action_high, dtype=np.float32)

        # The observation space contains:
        # 0. A measure of the cart's distance from the center, where 0 is at the center and +/-1 is at the limit.
        # 1. A measure of the angular distance of the pole from the upright position, where 0 is at the upright position and 1 is at the down position.
        # 2. The cart's current velocity (m/s).
        # 3. The pole's angular velocity (rad/s).
        observation_high = np.array([1, 1, np.finfo(np.float32).max, np.finfo(np.float32).max], dtype=np.float32)
        self.observation_space = gymnasium.spaces.Box(-observation_high, observation_high, dtype=np.float32)

    def reward(self, obs):
        distance = 1 - math.fabs(obs[0]) # How close the cart is to the center
        angle = 1 - math.fabs(obs[1]) # How close the pole is to the upright position
        force = math.fabs(self.get(address_cart_force)) # How much force is being applied to drive the cart's motor
        return (angle * angle) * 0.8 + (distance * distance) * 0.2 - force * 0.001
    
    def observations(self):
        cart_position = self.get(address_cart_position) # Read the current cart position
        cart_velocity = self.get(address_cart_velocity) # Read the current cart velocity
        pole_angle = self.get(address_pole_angle) # Read the current pole angle
        pole_angular_velocity = self.get(address_pole_angular_velocity) # Read the current pole angular velocity
        pole_angular_distance = math.atan2(math.sin(math.pi - pole_angle), math.cos(math.pi - pole_angle)) # Calculate angular distance from upright position
        return np.array([cart_position / self.x_threshold, pole_angular_distance / math.pi, cart_velocity, pole_angular_velocity])

    def reset(self, seed = None):
        super().reset(seed=seed)
        return self.observations(), {}
    
    def apply(self, action):
        self.set(address_cart_target_velocity, action[0]) # Apply action by setting the cart's target velocity

    def step(self):
        obs = self.observations()
        reward = self.reward(obs) # Calculate reward
        done = abs(obs[0]) > 1 # Terminate if cart goes beyond limits
        truncated = self.time > 20 # Truncate after 20 seconds
        return obs, reward, done, truncated, {}

# STEP 4: Setup the training session
async def main():
    # Start ProtoTwin Connect
    client = await prototwin.start()

    # Load the ProtoTwin model
    filepath = os.path.join(os.path.dirname(__file__), "CartPole.ptm")
    await client.load(filepath)

    # Create the vectorized environment
    observation_high = np.array([1, 1, 1, np.finfo(np.float32).max], dtype=np.float32)
    observation_space = gymnasium.spaces.Box(-observation_high, observation_high, dtype=np.float32)
    action_high = np.array([1.0], dtype=np.float32)
    action_space = gymnasium.spaces.Box(-action_high, action_high, dtype=np.float32)
    source_entity_name = "Main"
    instance_count = 64
    env = VecEnv(CartPoleEnv, client, source_entity_name, instance_count, observation_space, action_space)
    monitored = VecMonitor(env) # Monitor the training progress

    # Create callback to regularly save the model
    save_freq = 10000 # Number of timesteps per instance
    checkpoint_callback = CheckpointCallback(save_freq=save_freq, save_path="./logs/checkpoints/", name_prefix="checkpoint", save_replay_buffer=True, save_vecnormalize=True)

    # Start learning!
    model = PPO(stable_baselines3.ppo.MlpPolicy, monitored, device=torch.cuda.current_device(), verbose=1, batch_size=4096, n_steps=1000, learning_rate=0.0003, tensorboard_log="./tensorboard/")
    model.learn(total_timesteps=10_000_000, callback=checkpoint_callback)

asyncio.run(main())
```

## Exporting to ONNX

It is possible to export trained models to the ONNX format. This can be used to embed trained agents into ProtoTwin models for inferencing. Please refer to the [Stable Baselines exporting documentation](https://stable-baselines3.readthedocs.io/en/master/guide/export.html) for further details. The example provided below shows how to export the trained Cart Pole model to ONNX.

```
# Export to ONNX for embedding into ProtoTwin models using ONNX Runtime Web
def export():
    class OnnxableSB3Policy(th.nn.Module):
        def __init__(self, policy: BasePolicy):
            super().__init__()
            self.policy = policy

        def forward(self, observation: th.Tensor) -> Tuple[th.Tensor, th.Tensor, th.Tensor]:
            return self.policy(observation, deterministic=True)
    
    # Load the trained ML model
    model = PPO.load("logs/best_model/best_model", device="cpu")

    # Create the Onnx policy
    onnx_policy = OnnxableSB3Policy(model.policy)

    observation_size = model.observation_space.shape
    dummy_input = th.randn(1, *observation_size)
    th.onnx.export(onnx_policy, dummy_input, "CartPole.onnx", opset_version=17, input_names=["input"], output_names=["output"])
```

## Inference in ProtoTwin

It is possible to embed trained agents into ProtoTwin models. To do this, you must create a scripted component that loads the ONNX model, feeds observations into the model and finally applies the output actions. Note that this example assumes that the ONNX file has been included into the model by dragging the file into the script editor's file explorer. Alternatively, the ONNX file can be loaded from a URL.

```
import { type Entity, type Handle, InferenceComponent, MotorComponent, Util } from "prototwin";

export class CartPole extends InferenceComponent {
    public cartMotor: Handle<MotorComponent>;
    public poleMotor: Handle<MotorComponent>;
    
    constructor(entity: Entity) {
        super(entity);
        this.cartMotor = this.handle(MotorComponent);
        this.poleMotor = this.handle(MotorComponent);
    }

    public override async initializeAsync() {
        // Load the ONNX model from the local filesystem.
        this.loadModelFromFile("CartPole.onnx", 4, [-1], [1]);
    }

    public override async updateAsync() {
        const cartMotor = this.cartMotor.value;
        const poleMotor = this.poleMotor.value;
        const observations = this.observations;
        if (cartMotor === null || poleMotor === null || observations === null) { return; }

        // Populate observation array
        const cartPosition = cartMotor.currentPosition;
        const cartVelocity = cartMotor.currentVelocity;
        const poleAngularDistance = Util.signedAngularDifference(poleMotor.currentPosition, Math.PI);
        const poleAngularVelocity = poleMotor.currentVelocity;        
        observations[0] = cartPosition / 0.65;
        observations[1] = poleAngularDistance / Math.PI;
        observations[2] = cartVelocity;
        observations[3] = poleAngularVelocity;

        // Apply the actions
        const actions = await this.run();
        if (actions !== null) {
            cartMotor.targetVelocity = actions[0];
        }
    }
}
```