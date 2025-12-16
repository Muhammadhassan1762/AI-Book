#!/usr/bin/env python3

"""
Exercise 3 Solution: Create a simple service server and client.

Create a service that adds two integers and a client that calls the service.
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsService(Node):
    """
    Service server that adds two integers.
    """

    def __init__(self):
        super().__init__('add_two_ints_service')

        # Create a service that adds two integers
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )

        self.get_logger().info('Add Two Ints service is ready.')

    def add_two_ints_callback(self, request, response):
        """
        Callback function for the service.
        """
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {request.a} + {request.b} = {response.sum}')
        return response


class AddTwoIntsClient(Node):
    """
    Service client that calls the add_two_ints service.
    """

    def __init__(self):
        super().__init__('add_two_ints_client')

        # Create a client for the service
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for the service to be available
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        self.get_logger().info('Service client is ready.')

    def send_request(self, a, b):
        """
        Send a request to the service.
        """
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        # Call the service asynchronously
        self.future = self.cli.call_async(request)
        return self.future


def main_service(args=None):
    """
    Main function for the service server.
    """
    rclpy.init(args=args)

    service_node = AddTwoIntsService()

    try:
        rclpy.spin(service_node)
    except KeyboardInterrupt:
        pass

    service_node.destroy_node()
    rclpy.shutdown()


def main_client(args=None):
    """
    Main function for the service client.
    """
    rclpy.init(args=args)

    client_node = AddTwoIntsClient()

    # Send a request
    future = client_node.send_request(10, 20)

    try:
        # Wait for the response
        rclpy.spin_until_future_complete(client_node, future)

        if future.result() is not None:
            response = future.result()
            client_node.get_logger().info(f'Result of add_two_ints: {response.sum}')
        else:
            client_node.get_logger().info('Service call failed')
    except KeyboardInterrupt:
        pass

    client_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    # This file contains both service and client
    # To run the service: ros2 run ros2_fundamentals_examples exercise_3_solution_service
    # To run the client: ros2 run ros2_fundamentals_examples exercise_3_solution_client
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        main_client()
    else:
        main_service()