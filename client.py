import grpc
import temperature_pb2
import temperature_pb2_grpc
import matplotlib.pyplot as plt
from collections import defaultdict, deque
import math
from datetime import datetime


def create_plot(locations):
    """Initialize the plot with subplots for each location."""
    num_locations = len(locations)
    cols = 3  # Number of columns in the grid
    rows = math.ceil(num_locations / cols)  # Number of rows
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()  # Flatten the 2D array of axes for easy access

    # Initialize data containers and plot lines
    x_data = defaultdict(lambda: deque(maxlen=20))
    y_data = defaultdict(lambda: deque(maxlen=20))

    # Color palette for locations
    color_palette = plt.cm.tab10.colors  # A palette with 10 distinct colors
    lines = {}

    # Initialize the subplots
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

    return fig, axes, x_data, y_data, lines


def update_plot(fig, axes, lines, x_data, y_data, locations, response):
    """Update the plot with new temperature data."""
    location = response.location
    temperature = response.temperature
    timestamp_obj = datetime.fromisoformat(response.timestamp)
    formatted_time = timestamp_obj.strftime("%H:%M:%S")  # HH:MM:SS format

    # Update data
    x_data[location].append(formatted_time)
    y_data[location].append(temperature)

    # Update the plot for this location
    idx = locations.index(location)
    axes[idx].set_ylim(min(y_data[location]) - 5, max(y_data[location]) + 5)  # Auto-scale
    lines[location].set_xdata(range(len(x_data[location])))
    lines[location].set_ydata(y_data[location])
    axes[idx].set_xticks(range(len(x_data[location])))
    axes[idx].set_xticklabels(x_data[location], rotation=45, ha="right")

    # Refresh the plot
    fig.canvas.draw()
    fig.canvas.flush_events()


def run():
    # Define multiple locations to monitor
    locations = [
        "New York", "San Francisco", "London", "Tokyo", "Sydney", 
        "Berlin", "Mumbai", "Cape Town", "Rio de Janeiro", "Moscow"
    ]
    print(f"Requesting temperature data for: {', '.join(locations)}")

    # Set up dynamic plot
    fig, axes, x_data, y_data, lines = create_plot(locations)

    # Enable interactive mode for real-time updates
    plt.ion()

    # Connect to the server using gRPC
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = temperature_pb2_grpc.TemperatureServiceStub(channel)

        # Create streaming request for multiple locations
        requests = (temperature_pb2.TemperatureRequest(location=loc) for loc in locations)
        response_stream = stub.StreamTemperature(requests)

        try:
            for response in response_stream:
                update_plot(fig, axes, lines, x_data, y_data, locations, response)
                plt.pause(0.1)  # Pause to update the plot
        except grpc.RpcError as e:
            print(f"gRPC Error: {e}")
        finally:
            plt.ioff()  # Disable interactive mode once the stream ends
            plt.show()  # Display the final plot after stream ends


if __name__ == "__main__":
    run()
