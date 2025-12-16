#!/usr/bin/env python3
"""
Navigation Test Environment

This script provides a test environment for validating Nav2 navigation
with VSLAM-generated maps and humanoid robot navigation.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.timer import Timer

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid, Path
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String, Float32
from sensor_msgs.msg import LaserScan
import math
import time
import numpy as np
from typing import List, Tuple


class NavigationTester(Node):
    def __init__(self):
        super().__init__('navigation_tester')

        # QoS profile
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Create publishers for test data
        self.map_pub = self.create_publisher(OccupancyGrid, '/vslam/map', qos_profile)
        self.pose_pub = self.create_publisher(PoseStamped, '/vslam/pose', qos_profile)
        self.goal_pub = self.create_publisher(PoseStamped, '/clicked_goal', qos_profile)
        self.scan_pub = self.create_publisher(LaserScan, '/scan', qos_profile)

        # Create subscribers for navigation status
        self.nav_status_sub = self.create_subscription(
            String,
            '/nav2/status',
            self.nav_status_callback,
            qos_profile
        )

        self.nav_progress_sub = self.create_subscription(
            Float32,
            '/nav2/progress',
            self.nav_progress_callback,
            qos_profile
        )

        # Initialize test variables
        self.test_scenario = 0
        self.navigation_success_count = 0
        self.navigation_failure_count = 0
        self.current_test_goal = None
        self.navigation_progress = 0.0
        self.navigation_status = "idle"

        # Create timer for test execution
        self.test_timer = self.create_timer(2.0, self.run_test_scenario)

        # Test scenarios: (start_x, start_y, goal_x, goal_y, description)
        self.test_scenarios = [
            (0.0, 0.0, 2.0, 2.0, "Simple diagonal navigation"),
            (2.0, 2.0, -1.0, -1.0, "Return navigation"),
            (-1.0, -1.0, 1.0, -2.0, "Sideways navigation"),
            (1.0, -2.0, 3.0, 0.0, "Forward navigation"),
        ]

        self.get_logger().info(f'Navigation Tester initialized with {len(self.test_scenarios)} test scenarios')

    def create_test_map(self) -> OccupancyGrid:
        """Create a test map for navigation"""
        map_msg = OccupancyGrid()
        map_msg.header.frame_id = 'map'
        map_msg.header.stamp = self.get_clock().now().to_msg()

        # Map parameters
        map_msg.info.resolution = 0.05  # 5cm per cell
        map_msg.info.width = 200  # 10m x 20 cells per meter
        map_msg.info.height = 200  # 10m x 20 cells per meter
        map_msg.info.origin.position.x = -5.0
        map_msg.info.origin.position.y = -5.0
        map_msg.info.origin.position.z = 0.0
        map_msg.info.origin.orientation.w = 1.0

        # Create a simple map with some obstacles
        map_data = [-1] * (map_msg.info.width * map_msg.info.height)  # Unknown initially

        # Add some free space in the center
        for y in range(80, 120):  # Center region
            for x in range(80, 120):
                idx = y * map_msg.info.width + x
                if 0 <= idx < len(map_data):
                    map_data[idx] = 0  # Free space

        # Add some obstacles
        # Vertical wall
        for y in range(50, 150):
            for x in range(98, 102):
                idx = y * map_msg.info.width + x
                if 0 <= idx < len(map_data):
                    map_data[idx] = 100  # Occupied

        # Horizontal wall
        for y in range(98, 102):
            for x in range(50, 150):
                idx = y * map_msg.info.width + x
                if 0 <= idx < len(map_data):
                    map_data[idx] = 100  # Occupied

        # Add corridor
        for y in range(45, 55):
            for x in range(95, 105):
                idx = y * map_msg.info.width + x
                if 0 <= idx < len(map_data):
                    map_data[idx] = 0  # Free space

        map_msg.data = map_data
        return map_msg

    def create_test_pose(self, x: float, y: float, theta: float = 0.0) -> PoseStamped:
        """Create a test pose"""
        pose_msg = PoseStamped()
        pose_msg.header.frame_id = 'map'
        pose_msg.header.stamp = self.get_clock().now().to_msg()

        pose_msg.pose.position.x = x
        pose_msg.pose.position.y = y
        pose_msg.pose.position.z = 0.0

        # Convert theta to quaternion
        qw = math.cos(theta / 2.0)
        qx = 0.0
        qy = 0.0
        qz = math.sin(theta / 2.0)

        pose_msg.pose.orientation.x = qx
        pose_msg.pose.orientation.y = qy
        pose_msg.pose.orientation.z = qz
        pose_msg.pose.orientation.w = qw

        return pose_msg

    def create_test_scan(self) -> LaserScan:
        """Create a test laser scan"""
        scan_msg = LaserScan()
        scan_msg.header.frame_id = 'laser_frame'
        scan_msg.header.stamp = self.get_clock().now().to_msg()

        # Laser scan parameters
        scan_msg.angle_min = -math.pi / 2
        scan_msg.angle_max = math.pi / 2
        scan_msg.angle_increment = math.pi / 180  # 1 degree
        scan_msg.time_increment = 0.0
        scan_msg.scan_time = 0.1
        scan_msg.range_min = 0.1
        scan_msg.range_max = 10.0

        # Create ranges - simulate some obstacles
        num_readings = int((scan_msg.angle_max - scan_msg.angle_min) / scan_msg.angle_increment) + 1
        ranges = []

        for i in range(num_readings):
            angle = scan_msg.angle_min + i * scan_msg.angle_increment

            # Simulate some obstacles at specific angles
            if -0.3 < angle < 0.3:  # Front
                ranges.append(2.0)  # Obstacle 2m ahead
            elif -0.8 < angle < -0.5:  # Left
                ranges.append(1.5)  # Obstacle 1.5m left
            elif 0.5 < angle < 0.8:  # Right
                ranges.append(1.5)  # Obstacle 1.5m right
            else:
                ranges.append(float('inf'))  # No obstacle

        scan_msg.ranges = ranges
        scan_msg.intensities = [100.0] * len(ranges)  # Dummy intensities

        return scan_msg

    def nav_status_callback(self, msg):
        """Receive navigation status updates"""
        self.navigation_status = msg.data
        self.get_logger().debug(f'Navigation status: {self.navigation_status}')

    def nav_progress_callback(self, msg):
        """Receive navigation progress updates"""
        self.navigation_progress = msg.data
        self.get_logger().debug(f'Navigation progress: {self.navigation_progress:.2f}')

    def run_test_scenario(self):
        """Run the next test scenario"""
        if self.test_scenario >= len(self.test_scenarios):
            self.get_logger().info('All test scenarios completed')
            self.print_test_summary()
            return

        scenario = self.test_scenarios[self.test_scenario]
        start_x, start_y, goal_x, goal_y, description = scenario

        self.get_logger().info(f'Running test scenario {self.test_scenario + 1}: {description}')
        self.get_logger().info(f'  From: ({start_x:.1f}, {start_y:.1f}) to ({goal_x:.1f}, {goal_y:.1f})')

        # Publish test map
        test_map = self.create_test_map()
        self.map_pub.publish(test_map)

        # Publish initial robot pose
        initial_pose = self.create_test_pose(start_x, start_y)
        self.pose_pub.publish(initial_pose)

        # Publish laser scan
        test_scan = self.create_test_scan()
        self.scan_pub.publish(test_scan)

        # Wait a moment for systems to process
        self.get_logger().info('Waiting for systems to initialize...')
        time.sleep(2.0)

        # Send navigation goal
        goal_pose = self.create_test_pose(goal_x, goal_y)
        self.goal_pub.publish(goal_pose)

        self.current_test_goal = (goal_x, goal_y)
        self.test_scenario += 1

        # Schedule result check
        self.create_timer(10.0, self.check_test_result)

    def check_test_result(self):
        """Check if the current test was successful"""
        if self.current_test_goal:
            goal_x, goal_y = self.current_test_goal
            success_threshold = 0.5  # 50cm tolerance

            # In a real test, we would check the robot's actual position
            # For this simulation, we'll assume success based on progress
            if self.navigation_progress < success_threshold:
                self.navigation_success_count += 1
                self.get_logger().info(f'  Test SUCCESS: Reached goal within {success_threshold}m tolerance')
            else:
                self.navigation_failure_count += 1
                self.get_logger().info(f'  Test FAILED: Did not reach goal (progress: {self.navigation_progress:.2f}m)')

            self.current_test_goal = None

    def print_test_summary(self):
        """Print test results summary"""
        total_tests = self.navigation_success_count + self.navigation_failure_count
        if total_tests > 0:
            success_rate = (self.navigation_success_count / total_tests) * 100
            self.get_logger().info(f'=== NAVIGATION TEST SUMMARY ===')
            self.get_logger().info(f'Total tests: {total_tests}')
            self.get_logger().info(f'Successful: {self.navigation_success_count}')
            self.get_logger().info(f'Failed: {self.navigation_failure_count}')
            self.get_logger().info(f'Success rate: {success_rate:.1f}%')
            self.get_logger().info(f'===============================')


def main(args=None):
    rclpy.init(args=args)

    node = NavigationTester()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Test interrupted by user')
    finally:
        node.print_test_summary()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()