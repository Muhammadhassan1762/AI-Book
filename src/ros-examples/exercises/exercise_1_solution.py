#!/usr/bin/env python3

"""
Exercise 1 Solution: Create a publisher that publishes integers instead of strings.

Modify the basic_publisher.py to publish integer messages instead of strings.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32  # Changed from String to Int32


class Exercise1Solution(Node):
    """
    Solution for Exercise 1: Publisher that publishes integers.
    """

    def __init__(self):
        super().__init__('exercise_1_solution')

        # Create a publisher that will publish Int32 messages to the 'counter' topic
        self.publisher_ = self.create_publisher(Int32, 'counter', 10)

        # Create a timer that calls the timer_callback method every 1 second
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter to keep track of the number
        self.number = 0

        self.get_logger().info('Exercise 1 Solution node initialized.')

    def timer_callback(self):
        """
        Callback function that is called by the timer at regular intervals.
        Creates and publishes an integer message.
        """
        # Create an Int32 message
        msg = Int32()
        msg.data = self.number

        # Publish the message
        self.publisher_.publish(msg)

        # Log the message that was sent
        self.get_logger().info(f'Publishing: {msg.data}')

        # Increment the counter
        self.number += 1


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the publisher node,
    and spins to keep the node running until interrupted.
    """
    rclpy.init(args=args)

    exercise_node = Exercise1Solution()

    try:
        rclpy.spin(exercise_node)
    except KeyboardInterrupt:
        pass

    exercise_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()