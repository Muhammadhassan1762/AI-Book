#!/usr/bin/env python3

"""
AI Decision Node for ROS 2 fundamentals.

This node demonstrates how AI decision-making logic can be integrated with ROS 2.
It simulates an AI agent that makes decisions based on sensor input and sends
commands to a robot controller.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from geometry_msgs.msg import Twist
import random
import math


class AIDecisionNode(Node):
    """
    An AI decision node that processes sensor data and makes decisions
    about robot behavior, then sends commands to the robot controller.
    """

    def __init__(self):
        # Initialize the node with the name 'ai_decision_node'
        super().__init__('ai_decision_node')

        # Create subscription to receive sensor data (simulated)
        self.sensor_subscription = self.create_subscription(
            String,
            'sensor_data',
            self.sensor_callback,
            10
        )

        # Create publisher to send commands to the robot controller
        self.command_publisher = self.create_publisher(Twist, 'robot_cmd_vel', 10)

        # Create a timer to periodically make decisions (even without sensor input)
        self.timer = self.create_timer(0.5, self.decision_timer_callback)

        # Internal state for decision making
        self.last_sensor_data = None
        self.robot_state = {'x': 0.0, 'y': 0.0, 'theta': 0.0}  # Position and orientation
        self.target_position = {'x': 5.0, 'y': 5.0}  # Target to navigate to
        self.obstacle_detected = False

        self.get_logger().info('AI Decision Node initialized')

    def sensor_callback(self, msg):
        """
        Callback to process incoming sensor data.

        Args:
            msg: Sensor data message
        """
        self.get_logger().info(f'Received sensor data: {msg.data}')
        self.last_sensor_data = msg.data

        # Parse sensor data (in a real system, this would be more complex)
        if 'obstacle' in msg.data.lower():
            self.obstacle_detected = True
        else:
            self.obstacle_detected = False

    def decision_timer_callback(self):
        """
        Timer callback that makes decisions about robot behavior.
        """
        # Make a decision based on current state and sensor data
        command = self.make_decision()

        # Publish the command
        if command:
            self.command_publisher.publish(command)
            self.get_logger().info(f'Sent command: linear={command.linear.x}, angular={command.angular.z}')

    def make_decision(self):
        """
        Core AI decision-making logic.

        Returns:
            Twist: A velocity command for the robot, or None if no command
        """
        cmd = Twist()

        # Simple navigation algorithm to move toward target
        if self.obstacle_detected:
            # If obstacle detected, turn to avoid
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5  # Turn right
            self.get_logger().info('Obstacle detected - turning to avoid')
        else:
            # Calculate direction to target
            dx = self.target_position['x'] - self.robot_state['x']
            dy = self.target_position['y'] - self.robot_state['y']
            distance_to_target = math.sqrt(dx**2 + dy**2)
            target_angle = math.atan2(dy, dx)

            # Calculate angular error
            angle_error = target_angle - self.robot_state['theta']

            # Normalize angle error to [-pi, pi]
            while angle_error > math.pi:
                angle_error -= 2 * math.pi
            while angle_error < -math.pi:
                angle_error += 2 * math.pi

            # Simple proportional controller
            if abs(angle_error) > 0.1:  # If not facing target
                cmd.angular.z = max(min(angle_error * 1.0, 0.5), -0.5)  # Limit angular speed
                cmd.linear.x = 0.0  # Don't move forward while turning
            elif distance_to_target > 0.5:  # If not at target
                cmd.linear.x = min(distance_to_target * 0.5, 1.0)  # Move toward target
                cmd.angular.z = max(min(angle_error * 1.0, 0.5), -0.5)  # Correct orientation
            else:
                # At target, stop
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info('Reached target position!')

        return cmd

    def simulate_sensor_data(self):
        """
        Simulate sensor data for demonstration purposes.
        In a real system, this would come from actual sensors.
        """
        # Simulate different sensor conditions
        conditions = [
            "clear path ahead",
            "obstacle 1m ahead",
            "obstacle 2m ahead",
            "clear path ahead",
            "obstacle right side",
            "clear path ahead"
        ]
        return random.choice(conditions)


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the AI decision node,
    and spins to keep the node running until interrupted.
    """
    # Initialize the ROS 2 client library
    rclpy.init(args=args)

    # Create an instance of the AIDecisionNode
    ai_decision_node = AIDecisionNode()

    # Keep the node running until interrupted
    try:
        rclpy.spin(ai_decision_node)
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly
    ai_decision_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()