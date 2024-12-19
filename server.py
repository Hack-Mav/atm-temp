import time
import grpc
from concurrent import futures
from datetime import datetime
import temperature_pb2
import temperature_pb2_grpc
import random


class TemperatureServiceServicer(temperature_pb2_grpc.TemperatureServiceServicer):
    def __init__(self):
        self.active_locations = set()  # Keep track of the active locations.

    def StreamTemperature(self, request_iterator, context):
        """Streams temperature data for each active location."""
        # Collect active locations from the client requests
        for request in request_iterator:
            self._add_location(request.location)

        # Continuously generate and stream temperature data
        try:
            while True:
                for location in self.active_locations:
                    temperature_data = self._generate_temperature_data(location)
                    yield temperature_data
                time.sleep(1)  # Simulate real-time data generation
        except grpc.RpcError:
            print("Connection closed by the client.")

    def _add_location(self, location):
        """Adds a location to the active locations list."""
        self.active_locations.add(location)
        print(f"Started streaming for location: {location}")

    def _generate_temperature_data(self, location):
        """Generates random temperature data."""
        temperature = random.uniform(-10, 40)  # Simulated temperature in °C
        timestamp = datetime.utcnow().isoformat()  # Timestamp in UTC
        return temperature_pb2.TemperatureData(
            location=location,
            temperature=temperature,
            timestamp=timestamp
        )


def serve():
    """Starts the gRPC server and handles client connections."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    temperature_pb2_grpc.add_TemperatureServiceServicer_to_server(TemperatureServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051")
    server.start()

    # Keep the server running
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nServer interrupted and shutting down gracefully.")


if __name__ == "__main__":
    serve()
