#!/usr/bin/env python3

"""
Robot Controller Interface for ROS 2 fundamentals.

This node demonstrates how to interface with robot hardware/controllers
by receiving commands from an AI decision node and translating them
into actions for the robot.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import time


class RobotController(Node):
    """
    A robot controller that receives commands and interfaces with the robot's hardware.
    In simulation, this node will log the commands and potentially publish status updates.
    """

    def __init__(self):
        # Initialize the node with the name 'robot_controller'
        super().__init__('robot_controller')

        # Create subscription to receive velocity commands from AI decision node
        self.cmd_vel_subscription = self.create_subscription(
            Twist,
            'robot_cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Create publisher for status updates
        self.status_publisher = self.create_publisher(String, 'robot_status', 10)

        # Create publisher for simulated sensor data (to close the loop)
        self.sensor_publisher = self.create_publisher(String, 'sensor_data', 10)

        # Timer to periodically publish simulated sensor data
        self.sensor_timer = self.create_timer(1.0, self.publish_sensor_data)

        # Robot state tracking
        self.current_velocity = Twist()
        self.robot_position = {'x': 0.0, 'y': 0.0}
        self.last_command_time = self.get_clock().now()

        self.get_logger().info('Robot Controller initialized')

    def cmd_vel_callback(self, msg):
        """
        Callback to process incoming velocity commands.

        Args:
            msg: Twist message containing linear and angular velocities
        """
        self.get_logger().info(f'Received command - Linear: {msg.linear.x}, Angular: {msg.angular.z}')

        # Store the current command
        self.current_velocity = msg
        self.last_command_time = self.get_clock().now()

        # In a real robot, this is where you would send commands to the hardware
        # For simulation, we'll just log the command and update our internal state
        self.execute_command(msg)

        # Publish status update
        status_msg = String()
        status_msg.data = f"Executing: linear={msg.linear.x}, angular={msg.angular.z}"
        self.status_publisher.publish(status_msg)

    def execute_command(self, cmd):
        """
        Execute the given command (in simulation, just update internal state).

        Args:
            cmd: Twist message with the command to execute
        """
        # In a real robot, this would interface with hardware controllers
        # For simulation, we'll update position based on the command
        dt = 0.1  # Time step for simulation
        self.robot_position['x'] += cmd.linear.x * dt
        self.robot_position['y'] += cmd.linear.y * dt  # Usually 0 for differential drive

        # Update orientation based on angular velocity
        current_theta = 0  # In a real system, this would come from odometry
        new_theta = current_theta + cmd.angular.z * dt

        self.get_logger().info(f'Robot position: ({self.robot_position["x"]:.2f}, {self.robot_position["y"]:.2f})')

    def publish_sensor_data(self):
        """
        Publish simulated sensor data to provide feedback to the AI decision node.
        """
        # Simulate sensor data based on environment and robot state
        sensor_msg = String()

        # Simple simulation: sometimes report obstacles, sometimes clear path
        import random
        if random.random() < 0.3:  # 30% chance of obstacle
            sensor_msg.data = "obstacle 1m ahead"
        else:
            sensor_msg.data = "clear path ahead"

        self.sensor_publisher.publish(sensor_msg)
        self.get_logger().info(f'Published sensor data: {sensor_msg.data}')

    def get_robot_status(self):
        """
        Get current status of the robot.

        Returns:
            str: Current status description
        """
        current_time = self.get_clock().now()
        time_since_command = (current_time - self.last_command_time).nanoseconds / 1e9

        if time_since_command > 5.0:  # No command for 5 seconds
            return "idle"
        else:
            return "active"


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the robot controller,
    and spins to keep the node running until interrupted.
    """
    # Initialize the ROS 2 client library
    rclpy.init(args=args)

    # Create an instance of the RobotController
    robot_controller = RobotController()

    # Keep the node running until interrupted
    try:
        rclpy.spin(robot_controller)
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly
    robot_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()