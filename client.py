import grpc
import temperature_pb2
import temperature_pb2_grpc
import matplotlib.pyplot as plt
from collections import defaultdict, deque
import math

def run():
    # Connect to the server using SSL/TLS
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = temperature_pb2_grpc.TemperatureServiceStub(channel)

        # Define multiple locations to monitor
        locations = [
            "New York", "San Francisco", "London", "Tokyo", "Sydney", 
            "Berlin", "Mumbai", "Cape Town", "Rio de Janeiro", "Moscow"
        ]
        print(f"Requesting temperature data for: {', '.join(locations)}")

        # Prepare dynamic plot
        plt.ion()
        num_locations = len(locations)
        cols = 3  # Number of columns in the grid
        rows = math.ceil(num_locations / cols)  # Number of rows
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        axes = axes.flatten()  # Flatten the 2D array of axes for easy access

        # Initialize data containers and plot lines
        x_data = defaultdict(lambda: deque(maxlen=20))
        y_data = defaultdict(lambda: deque(maxlen=20))

        # Use a color palette from matplotlib
        color_palette = plt.cm.tab10.colors  # A palette with 10 distinct colors
        lines = {}

        for idx, location in enumerate(locations):
            axes[idx].set_title(location)
            axes[idx].set_ylim(-10, 50)  # Initial temperature range
            axes[idx].set_xlabel("Time")
            axes[idx].set_ylabel("Temperature (°C)")
            axes[idx].grid(True)

             # Assign a unique color to each location
            color = color_palette[idx % len(color_palette)]
            lines[location], = axes[idx].plot([], [], '-o', label=location, color=color)
            axes[idx].legend()

        # Hide unused subplots
        for idx in range(num_locations, len(axes)):
            axes[idx].axis("off")

        # Create streaming request
        requests = (temperature_pb2.TemperatureRequest(location=loc) for loc in locations)
        response_stream = stub.StreamTemperature(requests)

        try:
            for response in response_stream:
                location = response.location
                temperature = response.temperature
                timestamp = response.timestamp.split("T")[-1]

                # Update data
                x_data[location].append(timestamp)
                y_data[location].append(temperature)

                # Update plot
                idx = locations.index(location)
                axes[idx].set_ylim(min(y_data[location]) - 5, max(y_data[location]) + 5)  # Auto-scale
                lines[location].set_xdata(range(len(x_data[location])))
                lines[location].set_ydata(y_data[location])
                axes[idx].set_xticks(range(len(x_data[location])))
                axes[idx].set_xticklabels(x_data[location], rotation=45, ha="right")

                # Refresh the plot
                fig.canvas.draw()
                fig.canvas.flush_events()
        except grpc.RpcError as e:
            print(f"gRPC Error: {e}")
        finally:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    run()
