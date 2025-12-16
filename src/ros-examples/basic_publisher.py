#!/usr/bin/env python3

"""
Basic publisher node example for ROS 2 fundamentals.

This node demonstrates the basic concept of a publisher in ROS 2.
It publishes a simple string message to a topic at a regular interval.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BasicPublisher(Node):
    """
    A simple publisher node that sends messages to a topic.
    """

    def __init__(self):
        # Initialize the node with the name 'basic_publisher'
        super().__init__('basic_publisher')

        # Create a publisher that will publish String messages to the 'chatter' topic
        # with a queue size of 10
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Create a timer that calls the timer_callback method every 0.5 seconds (2 Hz)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter to keep track of the number of messages sent
        self.i = 0

        # Log that the publisher has started
        self.get_logger().info('Basic Publisher node initialized.')

    def timer_callback(self):
        """
        Callback function that is called by the timer at regular intervals.
        Creates and publishes a message.
        """
        # Create a String message
        msg = String()
        msg.data = f'Hello World: {self.i}'

        # Publish the message
        self.publisher_.publish(msg)

        # Log the message that was sent
        self.get_logger().info(f'Publishing: "{msg.data}"')

        # Increment the counter
        self.i += 1


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the publisher node,
    and spins to keep the node running until interrupted.
    """
    # Initialize the ROS 2 client library
    rclpy.init(args=args)

    # Create an instance of the BasicPublisher node
    basic_publisher = BasicPublisher()

    # Keep the node running until interrupted
    try:
        rclpy.spin(basic_publisher)
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    basic_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()