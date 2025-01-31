import os
import logging
import traci
from dotenv import load_dotenv
from sumo_rl import SumoEnvironment
from stable_baselines3 import DQN
import matplotlib.pyplot as plt
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.logger import configure
from utils.sumo_config import sumo_cfg

# Load environment variables
load_dotenv()

# Configure paths
cfg_file = sumo_cfg['cfg_file']
net_file = sumo_cfg['net_file']
route_file = sumo_cfg['route_file']
add_file = sumo_cfg['add_file']


# Custom reward function (ensure it's defined based on your traffic management goals)
def custom_reward(ts):
    queue_length = ts.get_total_queued()
    avg_speed = sum([traci.lane.getLastStepMeanSpeed(lane) for lane in ts.lanes]) / len(ts.lanes)
    return -queue_length + avg_speed  # Example: prioritize reducing queue length and increasing speed

# Initialize environment
env = SumoEnvironment(
    net_file=net_file,
    route_file=route_file,
    #observation_class=CustomObservationFunction(),
    use_gui=False,  # Cambiar a True si se desea visualizar
    num_seconds=200,  # Increase the duration of each episode
    delta_time=5,
    yellow_time=3,
    min_green=8,
    max_green=50,
    single_agent=True,
    # time_to_teleport=60,
    #reward_fn='diff-waiting-time',  # Función de recompensa por defecto
    #reward_fn=custom_reward,
    sumo_seed="random",
    sumo_warnings=True,
    out_csv_name='outputs/traffic.csv',
    additional_sumo_cmd=f"-c {cfg_file} -a {add_file} --log sumo_traci_log.txt",
    add_per_agent_info=True,
    add_system_info=True
)


# Initialize and configure logger
log_dir = "./tensorboard_logs/"
os.makedirs(log_dir, exist_ok=True)
logger = configure(log_dir, ["stdout", "csv", "tensorboard"])

# Initialize DQN model
model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir)

# Train model
model.learn(total_timesteps=10000)

# Save model
model.save("dqn_sumo_traffic_optimizer")