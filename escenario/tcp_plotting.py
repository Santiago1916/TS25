import traci
import matplotlib.pyplot as plt
import time

# Start SUMO with TraCI
sumoCmd = ["sumo", "-c", "osm2.sumocfg"]
traci.start(sumoCmd)

# Set up the plot
plt.ion()  # Interactive mode on
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot(x_data, y_data, 'r-')

# Main loop for collecting and plotting data
try:
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()  # Advance simulation step

        # Collect data (e.g., vehicle speed)
        vehicle_ids = traci.vehicle.getIDList()
        if vehicle_ids:
            speed = traci.vehicle.getSpeed(vehicle_ids[0])
            x_data.append(time.time())
            y_data.append(speed)

            # Update plot
            line.set_xdata(x_data)
            line.set_ydata(y_data)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.001)

finally:
    traci.close()
    plt.ioff()  # Interactive mode off
    plt.show()
