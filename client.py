import grpc
import temperature_pb2
import temperature_pb2_grpc
import matplotlib.pyplot as plt
from collections import defaultdict, deque
from itertools import cycle
import time

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = temperature_pb2_grpc.TemperatureServiceStub(channel)

        # Define locations to monitor
        locations = ["New York", "San Francisco", "London"]
        print(f"Requesting temperature data for: {', '.join(locations)}")

        # Prepare real-time plot
        plt.ion()  # Enable interactive mode
        fig, ax = plt.subplots()
        x_data = defaultdict(lambda: deque(maxlen=20))  # Store timestamps for each location
        y_data = defaultdict(lambda: deque(maxlen=20))  # Store temperatures for each location

        color_cycle = cycle(plt.cm.tab10.colors)  # Generate a unique color for each location
        lines = {
            location: ax.plot([], [], '-o', label=location, color=next(color_cycle))[0]
            for location in locations
        }

        ax.set_ylim(-10, 50)  # Adjust temperature range
        ax.set_xlabel("Time")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()

        # Stream temperature data for all locations
        requests = (temperature_pb2.TemperatureRequest(location=loc) for loc in locations)
        response_stream = stub.StreamTemperature(requests)

        try:
            for response in response_stream:
                timestamp = response.timestamp.split("T")[-1]  # Extract time
                location = response.location
                temperature = response.temperature

                # Update data for this location
                x_data[location].append(timestamp)
                y_data[location].append(temperature)

                # Update plot line for this location
                line = lines[location]
                line.set_xdata(range(len(x_data[location])))
                line.set_ydata(y_data[location])
                ax.set_xticks(range(max(len(x) for x in x_data.values())))
                ax.set_xticklabels(
                    x_data[location], rotation=45, ha="right", fontsize=8
                )
                ax.relim()
                ax.autoscale_view()

                plt.pause(0.1)  # Allow updates
        except grpc.RpcError as e:
            print(f"gRPC Error: {e}")
        finally:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    run()
