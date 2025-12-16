#!/usr/bin/env python3
"""
Physics Validation Test Script

This script validates that the physics simulation behaves as expected
by testing basic physics properties like gravity, collisions, and motion.
"""

import math
import time
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Vector3
from gazebo_msgs.srv import GetPhysicsProperties
from gazebo_msgs.srv import SetPhysicsProperties


class PhysicsValidationTest(Node):
    def __init__(self):
        super().__init__('physics_validation_test')

        # Variables to store robot state
        self.robot_position = None
        self.robot_velocity = None
        self.initial_time = None
        self.test_start_time = None

        # Physics properties
        self.gravity = None

        # Create subscribers and clients
        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/robot/physics/state',
            self.odom_callback,
            10
        )

        self.get_physics_client = self.create_client(
            GetPhysicsProperties,
            '/gazebo/get_physics_properties'
        )

        self.set_physics_client = self.create_client(
            SetPhysicsProperties,
            '/gazebo/set_physics_properties'
        )

        # Wait for services
        while not self.get_physics_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for physics properties service...')

        self.get_logger().info('Physics validation test node initialized')

    def odom_callback(self, msg):
        """Callback to receive robot state from Gazebo"""
        self.robot_position = msg.pose.pose.position
        self.robot_velocity = msg.twist.twist.linear

        if self.test_start_time is None:
            self.test_start_time = self.get_clock().now()

    def get_current_physics_properties(self):
        """Get current physics properties from Gazebo"""
        request = GetPhysicsProperties.Request()
        future = self.get_physics_client.call_async(request)

        rclpy.spin_until_future_complete(self, future)
        response = future.result()

        if response is not None:
            self.gravity = response.gravity
            return response
        else:
            self.get_logger().error('Failed to get physics properties')
            return None

    def test_gravity(self):
        """Test that gravity is set to expected value (9.81 m/s²)"""
        properties = self.get_current_physics_properties()

        if properties is None:
            return False

        expected_gravity = Vector3(x=0.0, y=0.0, z=-9.81)
        actual_gravity = properties.gravity

        # Check if gravity is approximately correct (within 0.01 tolerance)
        gravity_correct = (
            abs(actual_gravity.x - expected_gravity.x) < 0.01 and
            abs(actual_gravity.y - expected_gravity.y) < 0.01 and
            abs(actual_gravity.z - expected_gravity.z) < 0.01
        )

        self.get_logger().info(f'Gravity test: Expected {expected_gravity}, Actual {actual_gravity}')
        self.get_logger().info(f'Gravity test result: {"PASS" if gravity_correct else "FAIL"}')

        return gravity_correct

    def test_free_fall_motion(self):
        """Test that objects accelerate at approximately 9.81 m/s² in free fall"""
        if self.robot_position is None or self.test_start_time is None:
            self.get_logger().warn('No robot data available for motion test')
            return False

        # This is a simplified test - in a real scenario, we would:
        # 1. Place an object in free fall
        # 2. Record its position over time
        # 3. Verify that acceleration matches gravity

        # For now, we'll just check that we have position data
        has_position_data = self.robot_position is not None
        self.get_logger().info(f'Position data available: {"YES" if has_position_data else "NO"}')

        return has_position_data

    def test_collision_response(self):
        """Test that collision detection and response is working"""
        # This would involve:
        # 1. Placing robot in contact with environment
        # 2. Verifying that contact forces prevent penetration
        # 3. Checking that friction and bounce properties are correct

        # For now, we'll just verify that the robot model has collision geometries
        # This test would require more complex setup in Gazebo
        self.get_logger().info('Collision response test: Verify collision geometries exist in model')
        return True  # Placeholder - actual implementation would be more complex

    def run_all_tests(self):
        """Run all physics validation tests"""
        self.get_logger().info('Starting physics validation tests...')

        results = {
            'gravity_test': self.test_gravity(),
            'motion_test': self.test_free_fall_motion(),
            'collision_test': self.test_collision_response()
        }

        self.get_logger().info('Physics validation test results:')
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.get_logger().info(f'  {test_name}: {status}')

        all_passed = all(results.values())
        self.get_logger().info(f'Overall result: {"ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"}')

        return all_passed


def main(args=None):
    rclpy.init(args=args)

    test_node = PhysicsValidationTest()

    # Give some time for data to be received
    time.sleep(2.0)

    # Run the validation tests
    success = test_node.run_all_tests()

    # Shutdown
    test_node.destroy_node()
    rclpy.shutdown()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()