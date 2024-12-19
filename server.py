import time
import grpc
from concurrent import futures
from datetime import datetime
import temperature_pb2
import temperature_pb2_grpc
import random


class TemperatureServiceServicer(temperature_pb2_grpc.TemperatureServiceServicer):
    def StreamTemperature(self, request_iterator, context):
        active_locations = set()
        for request in request_iterator:
            active_locations.add(request.location)
            print(f"Started streaming for location: {request.location}")

        while True:
            for location in active_locations:
                temperature = random.uniform(-10, 40)
                timestamp = datetime.utcnow().isoformat()

                yield temperature_pb2.TemperatureData(
                    location=location,
                    temperature=temperature,
                    timestamp=timestamp
                )
            time.sleep(1)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    temperature_pb2_grpc.add_TemperatureServiceServicer_to_server(TemperatureServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
