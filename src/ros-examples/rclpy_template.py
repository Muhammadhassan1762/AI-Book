#!/usr/bin/env python3

"""
Template for creating ROS 2 nodes with rclpy.

This file serves as a template for creating new ROS 2 nodes using the rclpy library.
It includes the basic structure and common patterns used in ROS 2 node development.
"""

import rclpy
from rclpy.node import Node


class RclpyNodeTemplate(Node):
    """
    A template class for creating ROS 2 nodes with rclpy.

    This class demonstrates the basic structure of a ROS 2 node and includes
    common patterns for initialization, parameter handling, publisher/subscriber
    creation, and lifecycle management.
    """

    def __init__(self):
        """
        Initialize the node with a name and set up components.
        """
        # Initialize the parent Node class with a node name
        super().__init__('rclpy_node_template')

        # Example: Declare parameters with default values
        # self.declare_parameter('param_name', 'default_value')
        # param_value = self.get_parameter('param_name').value

        # Example: Create a publisher (uncomment and modify as needed)
        # from std_msgs.msg import String
        # self.publisher_ = self.create_publisher(String, 'topic_name', 10)

        # Example: Create a subscriber (uncomment and modify as needed)
        # self.subscription = self.create_subscription(
        #     String,
        #     'topic_name',
        #     self.subscription_callback,
        #     10
        # )

        # Example: Create a timer (uncomment and modify as needed)
        # timer_period = 0.5  # seconds
        # self.timer = self.create_timer(timer_period, self.timer_callback)

        # Log that the node has been initialized
        self.get_logger().info('Rclpy Node Template initialized')

    def subscription_callback(self, msg):
        """
        Example callback function for handling incoming messages.

        Args:
            msg: The received message
        """
        self.get_logger().info(f'Received message: {msg}')

    def timer_callback(self):
        """
        Example callback function for handling timer events.
        """
        # Example: Publish a message if you have a publisher
        # msg = String()
        # msg.data = 'Hello from timer'
        # self.publisher_.publish(msg)
        # self.get_logger().info('Publishing: "%s"' % msg.data)

    def cleanup(self):
        """
        Perform any necessary cleanup before node shutdown.
        """
        self.get_logger().info('Cleaning up node resources')


def main(args=None):
    """
    Main function that initializes the node and runs it.

    Args:
        args: Command line arguments
    """
    # Initialize the ROS client library
    rclpy.init(args=args)

    # Create an instance of the node
    node = RclpyNodeTemplate()

    try:
        # Keep the node running until it's shut down
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Perform cleanup before exiting
        node.cleanup()
        # Shutdown the ROS client library
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()