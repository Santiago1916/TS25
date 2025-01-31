import os
import sys
import numpy as np
import random
import traci


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")



# Q-learning parameters
## todo: Make interface for this 
alpha = 0.1
gamma = 0.9
epsilon = 0.1
num_episodes = 1000


