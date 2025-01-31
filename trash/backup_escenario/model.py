import os
import sys
import traci
import sumolib
import gymnasium as gym
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from gymnasium import spaces
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SUMO_HOME must exist as env var 
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Declare env variable SUDO_HOME in .env or system variable")



# Gym Sumo Environment 
class SumoEnv(gym.Env):
    def __init__self(self, net_file, route_file, add_file, use_gui=True):
        super(SumoEnv, self).__init__()

        self.net_file = net_file
        self.route_file = route_file
        self.add_file = add_file
        self.use_gui = use_gui

        # sumo binary
        sumo_bin = 'sumo-gui' if self.use_gui else 'sumo'
        self.sumo_cmd = [sumo_bin, '-c', self.net_file, '-r', self.route_file, '-a', self.add_file]

        
        # Action and Observation Space
        self.action_space = spaces.Discrete(2) # for traffic lights then: 0 = red, 1 = green
        self.observation_space = spaces.Box(low=0, high=1, shape=(8,), dtype=np.float32) # 8 lanes in the network
        # for n lanes: get lanes of the network and create a box with n lanes

        def reset(self):
            traci.start(self.sumo_cmd)
            return self._get_observation()
        
        def step(self, action):
            # apply action
            self._apply_action(action)

            #advance the simulation
            traci.simulationStep

            # observe, reward and done
            obs = self._get_observation()
            reward = self._get_reward()
            done = self._is_done()

            return obs, reward, done, {}
        

        def _apply_action(self, action):
            pass
            # set the traffic lights
            # if action == 0:
                # traci.trafficlight.setRedYellowGreenState("0", "rrrrrrrr")
            # elif action == 1:
                # traci.trafficlight.setRedYellowGreenState("0", "gggggggg")
        
        def _get_observation(self):
            # get the number of vehicles in each lane
            # return the number of vehicles in each lane

            # logic for getting the observation
            obs = np.zeros(8) # example obs
            return obs
            #pass

        def _get_reward(self):
            # get the reward
            # return the reward
            reward = 0 
            return reward
        
    
        def _is_done(self):
            # logic for determining if the episode is done
            done = False
            return done
        
        def close(self):
            traci.close()

        


## SUMO environment
            
net_file = "../escenario/osm.net.xml.gz"
route_file = "../escenario/osm.passenger.trips.xml"
add_file = "../escenario/tls.xml"
env = SumoEnv(net_file, route_file, add_file, use_gui=True)
# detectors file ?


# Wrap Environment
env = DummyVecEnv([lambda: env])

# DQN Model
# DQN: Deep Q-Network
model = DQN('MlpPolicy', env, verbose=1)

## Train Model
model.learn(total_timesteps=10000)

########
# save model

model.save("dqn_sumo_traffic_optimizer")





### Visualization
def plot_traffic_density():
    traffic_density = [random.randint(0,100) for _ in range(100)]
    plt.plot(traffic_density)
    plt.xlabel('Time')
    plt.ylabel('Traffic Density')
    plt.tile('Traffic Density over Time')
    plt.show()


plot_traffic_density()