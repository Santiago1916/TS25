import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci

class TrafficControlEnv(gym.Env):
    def __init__(self, reward_fn=None):
        super(TrafficControlEnv, self).__init__()

        self.reward_function = reward_fn

        # Define the lanes grouped by their street directions
        self.lanes_by_street = {
            "E": ["E_0", "E_1", "E_2"],  # Eastbound lanes
            "N": ["N_0", "N_1", "N_2"],  # Northbound lanes
            "S": ["S_0", "S_1", "S_2"],  # Southbound lanes
            "W": ["W_0", "W_1", "W_2"]   # Westbound lanes
        }

        # Get IDs of E1 induction loops and E2 lane area detectors
        self.e1_sensors = traci.inductionloop.getIDList()
        self.e2_sensors = traci.lanearea.getIDList()
        self.traffic_light_id = "semaforos"  # ID of the controlled traffic light



        # Define observation space for the environment
        self.observation_space = spaces.Dict({
            "traffic_lights": spaces.Dict({
                "phase": spaces.Discrete(8),  # Traffic light phases (0-7)
                "duration": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),  # Phase duration
            }),
            "lanes": spaces.Dict({
                "queue_length": spaces.Box(low=0, high=50, shape=(len(self.lanes_by_street) * 3,), dtype=np.float32),  # Queue lengths per lane
                "waiting_time": spaces.Box(low=0, high=500, shape=(len(self.lanes_by_street) * 3,), dtype=np.float32),  # Waiting times per lane
            }),
            "sensors": spaces.Dict({
                "e1": spaces.Box(low=0, high=100, shape=(len(self.e1_sensors),), dtype=np.float32),  # Data from E1 sensors
                "e2": spaces.Box(low=0, high=100, shape=(len(self.e2_sensors),), dtype=np.float32),  # Data from E2 sensors
            }),
        })

        # Define action space: control phase and adjust duration
        self.action_space = spaces.Tuple((
            spaces.Discrete(8),  # Phase index (0-7)
            spaces.Discrete(3)  # Duration adjustment (-1, 0, +1)
        ))

    def reset(self):
        """Reset the environment and return the initial observation."""
        # Load the SUMO configuration file
        traci.start(["sumo", "-c", "../escenario/osm2.sumocfg"])  # Start SUMO
        traci.simulationStep()  # Step simulation to initialize
        return self.get_observation()

    def step(self, action):
        """Perform the given action and return the observation, reward, done, and info."""
        phase, duration_adjustment = action  # Unpack the action tuple
        self.apply_action(phase, duration_adjustment)  # Apply the action

        # Advance the simulation by one step
        traci.simulationStep()

        # Collect observations after the action
        observation = self.get_observation()

        # Calculate the reward based on the current observation
        reward = self.reward_function(observation) if self.reward_function else 0

        # Check if the simulation is finished
        done = traci.simulation.getMinExpectedNumber() == 0

        return observation, reward, done, {}

    def get_observation(self):
        """Retrieve the current state of the environment."""
        observation = {
            "traffic_lights": {
                # Current phase index of the traffic light
                "phase": traci.trafficlight.getPhase(self.traffic_light_id),
                # Duration of the current phase
                "duration": np.array([traci.trafficlight.getPhaseDuration(self.traffic_light_id)], dtype=np.float32),
            },
            "lanes": {
                # Queue lengths (number of halted vehicles) for each lane
                "queue_length": np.array([
                    traci.lane.getLastStepHaltingNumber(lane_id)
                    for direction in self.lanes_by_street.values()
                    for lane_id in direction
                ], dtype=np.float32),
                # Total waiting time (sum of waiting times of all vehicles) for each lane
                "waiting_time": np.array([
                    sum(traci.vehicle.getAccumulatedWaitingTime(veh_id)
                        for veh_id in traci.lane.getLastStepVehicleIDs(lane_id))
                    for direction in self.lanes_by_street.values()
                    for lane_id in direction
                ], dtype=np.float32),
            },
            "sensors": {
                # Vehicle counts from E1 induction loop sensors
                "e1": np.array([
                    traci.inductionloop.getLastStepVehicleNumber(sensor_id)
                    for sensor_id in self.e1_sensors
                ], dtype=np.float32),
                # Vehicle counts from E2 lane area sensors
                "e2": np.array([
                    traci.lanearea.getLastStepVehicleNumber(sensor_id)
                    for sensor_id in self.e2_sensors
                ], dtype=np.float32),
            },
        }
        return observation

    def apply_action(self, phase, duration_adjustment):
        """Apply the selected phase and adjust the duration."""
        # Get the current phase duration
        current_duration = traci.trafficlight.getPhaseDuration(self.traffic_light_id)
        # Calculate the new phase duration (minimum of 5 seconds)
        new_duration = max(5, current_duration + (5 * (duration_adjustment - 1)))

        # Set the traffic light to the specified phase
        traci.trafficlight.setPhase(self.traffic_light_id, phase)
        # Update the phase duration
        traci.trafficlight.setPhaseDuration(self.traffic_light_id, new_duration)

    def close(self):
        """Clean up the environment."""
        traci.close()  # Close the TraCI connection

# Example of a reward function
def reward_minimize_waiting_time(observation):
    """Reward function to minimize total waiting time across all lanes."""
    return -np.sum(observation["lanes"]["waiting_time"])

if __name__ == "__main__":
    # Test the environment
    env = TrafficControlEnv(reward_fn=reward_minimize_waiting_time)
    obs = env.reset()
    print("Initial Observation:", obs)

    for _ in range(10):
        action = env.action_space.sample()  # Sample a random action
        obs, reward, done, _ = env.step(action)
        print("Action:", action)
        print("Observation:", obs)
        print("Reward:", reward)

        if done:
            print("Simulation finished.")
            break

    env.close()
