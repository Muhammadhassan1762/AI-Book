#!/usr/bin/env python3

"""
Basic subscriber node example for ROS 2 fundamentals.

This node demonstrates the basic concept of a subscriber in ROS 2.
It subscribes to a topic and logs the messages it receives.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BasicSubscriber(Node):
    """
    A simple subscriber node that receives messages from a topic.
    """

    def __init__(self):
        # Initialize the node with the name 'basic_subscriber'
        super().__init__('basic_subscriber')

        # Create a subscription to the 'chatter' topic with String messages
        # The callback function 'listener_callback' will be called when a message is received
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)  # queue size of 10

        # Make sure the subscription is not destroyed when this function exits
        self.subscription  # prevent unused variable warning

        # Log that the subscriber has started
        self.get_logger().info('Basic Subscriber node initialized.')

    def listener_callback(self, msg):
        """
        Callback function that is called when a message is received on the 'chatter' topic.
        Logs the received message.
        """
        # Log the received message
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the subscriber node,
    and spins to keep the node running until interrupted.
    """
    # Initialize the ROS 2 client library
    rclpy.init(args=args)

    # Create an instance of the BasicSubscriber node
    basic_subscriber = BasicSubscriber()

    # Keep the node running until interrupted
    try:
        rclpy.spin(basic_subscriber)
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    basic_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()