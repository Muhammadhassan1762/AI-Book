#!/usr/bin/env python3

"""
Exercise 2 Solution: Create a subscriber that processes integer messages.

Modify the basic_subscriber.py to process integer messages and perform calculations.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32  # Changed from String to Int32


class Exercise2Solution(Node):
    """
    Solution for Exercise 2: Subscriber that processes integer messages.
    """

    def __init__(self):
        super().__init__('exercise_2_solution')

        # Create a subscription to the 'counter' topic with Int32 messages
        self.subscription = self.create_subscription(
            Int32,
            'counter',
            self.listener_callback,
            10)

        # Make sure the subscription is not destroyed when this function exits
        self.subscription  # prevent unused variable warning

        # Track statistics
        self.message_count = 0
        self.sum_of_values = 0
        self.average = 0

        self.get_logger().info('Exercise 2 Solution node initialized.')

    def listener_callback(self, msg):
        """
        Callback function that is called when an Int32 message is received.
        Processes the message and calculates statistics.
        """
        # Update statistics
        self.message_count += 1
        self.sum_of_values += msg.data
        self.average = self.sum_of_values / self.message_count

        # Log the received message and calculated statistics
        self.get_logger().info(
            f'Received: {msg.data}, '
            f'Count: {self.message_count}, '
            f'Sum: {self.sum_of_values}, '
            f'Average: {self.average:.2f}'
        )


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the subscriber node,
    and spins to keep the node running until interrupted.
    """
    rclpy.init(args=args)

    exercise_node = Exercise2Solution()

    try:
        rclpy.spin(exercise_node)
    except KeyboardInterrupt:
        pass

    exercise_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()