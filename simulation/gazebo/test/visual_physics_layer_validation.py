#!/usr/bin/env python3
"""
Visual vs Physics Layer Validation Script

This script validates that the visual and physics layers are properly separated
and synchronized in the digital twin system.
"""

import time
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from std_srvs.srv import Trigger


class VisualPhysicsLayerValidation(Node):
    def __init__(self):
        super().__init__('visual_physics_layer_validation')

        # Variables to store data from both layers
        self.physics_state = None
        self.visual_state = None
        self.sync_status = None
        self.last_sync_time = None

        # Timing and synchronization data
        self.physics_timestamp = None
        self.visual_timestamp = None

        # Create subscribers for both physics and visual layers
        self.physics_subscriber = self.create_subscription(
            Odometry,
            '/robot/physics/state',
            self.physics_callback,
            10
        )

        self.visual_subscriber = self.create_subscription(
            PoseStamped,
            '/robot/visual/state',
            self.visual_callback,
            10
        )

        self.sync_status_subscriber = self.create_subscription(
            String,
            '/twin/sync_status',
            self.sync_status_callback,
            10
        )

        # Create service client for sync testing
        self.sync_now_client = self.create_client(
            Trigger,
            '/twin/sync_now'
        )

        # Wait for services
        while not self.sync_now_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for sync_now service...')

        self.get_logger().info('Visual vs Physics layer validation node initialized')

    def physics_callback(self, msg):
        """Callback to receive physics state from Gazebo"""
        self.physics_state = msg
        self.physics_timestamp = self.get_clock().now()

    def visual_callback(self, msg):
        """Callback to receive visual state from Unity"""
        self.visual_state = msg
        self.visual_timestamp = self.get_clock().now()

    def sync_status_callback(self, msg):
        """Callback to receive synchronization status"""
        self.sync_status = msg.data
        self.last_sync_time = self.get_clock().now()

    def validate_layer_separation(self):
        """Validate that physics and visual layers are properly separated"""
        # Check that both layers are publishing data
        physics_data_available = self.physics_state is not None
        visual_data_available = self.visual_state is not None

        self.get_logger().info(f'Physics layer data available: {"YES" if physics_data_available else "NO"}')
        self.get_logger().info(f'Visual layer data available: {"YES" if visual_data_available else "NO"}')

        # Both layers should be active
        layers_active = physics_data_available and visual_data_available

        if layers_active:
            self.get_logger().info('Layer separation validation: Both layers are active')
        else:
            self.get_logger().error('Layer separation validation: One or both layers are not active')

        return layers_active

    def validate_synchronization(self):
        """Validate that layers are properly synchronized"""
        if self.physics_state is None or self.visual_state is None:
            self.get_logger().warn('Insufficient data for synchronization validation')
            return False

        # Get positions from both layers
        physics_pos = self.physics_state.pose.pose.position
        visual_pos = self.visual_state.pose.position

        # Calculate distance between physics and visual positions
        distance = ((physics_pos.x - visual_pos.x)**2 +
                   (physics_pos.y - visual_pos.y)**2 +
                   (physics_pos.z - visual_pos.z)**2)**0.5

        # Define acceptable synchronization tolerance (in meters)
        sync_tolerance = 0.1  # 10 cm tolerance

        is_synchronized = distance < sync_tolerance

        self.get_logger().info(f'Physics position: ({physics_pos.x:.3f}, {physics_pos.y:.3f}, {physics_pos.z:.3f})')
        self.get_logger().info(f'Visual position: ({visual_pos.x:.3f}, {visual_pos.y:.3f}, {visual_pos.z:.3f})')
        self.get_logger().info(f'Position difference: {distance:.3f} m')
        self.get_logger().info(f'Synchronization tolerance: {sync_tolerance} m')
        self.get_logger().info(f'Synchronization validation: {"PASS" if is_synchronized else "FAIL"}')

        return is_synchronized

    def validate_timing_differences(self):
        """Validate that layers can have different update rates as expected"""
        if self.physics_timestamp is None or self.visual_timestamp is None:
            return False

        # In a properly designed system, physics and visual layers may have different update rates
        # This test verifies that timing differences are within expected ranges

        # For simulation: physics typically runs at 1000Hz, visuals at 30-60Hz
        # So we expect physics updates to be more frequent

        time_diff = abs((self.physics_timestamp.nanoseconds - self.visual_timestamp.nanoseconds) / 1e9)
        reasonable_diff = time_diff < 1.0  # Less than 1 second difference is reasonable

        self.get_logger().info(f'Time difference between layers: {time_diff:.3f} seconds')
        self.get_logger().info(f'Timing validation: {"PASS" if reasonable_diff else "FAIL"}')

        return reasonable_diff

    def test_manual_synchronization(self):
        """Test the manual synchronization service"""
        request = Trigger.Request()
        future = self.sync_now_client.call_async(request)

        rclpy.spin_until_future_complete(self, future)
        response = future.result()

        if response is not None:
            success = response.success
            message = response.message

            self.get_logger().info(f'Manual sync result: {success}')
            self.get_logger().info(f'Message: {message}')

            return success
        else:
            self.get_logger().error('Failed to call sync_now service')
            return False

    def run_validation_tests(self):
        """Run all visual vs physics layer validation tests"""
        self.get_logger().info('Starting visual vs physics layer validation tests...')

        # Wait a bit for data to accumulate
        time.sleep(2.0)

        results = {
            'layer_separation': self.validate_layer_separation(),
            'synchronization': self.validate_synchronization(),
            'timing_validation': self.validate_timing_differences(),
            'manual_sync_test': self.test_manual_synchronization()
        }

        self.get_logger().info('Visual vs Physics layer validation results:')
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.get_logger().info(f'  {test_name}: {status}')

        all_passed = all(results.values())
        self.get_logger().info(f'Overall validation result: {"ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"}')

        return all_passed


def main(args=None):
    rclpy.init(args=args)

    validation_node = VisualPhysicsLayerValidation()

    # Run the validation tests
    success = validation_node.run_validation_tests()

    # Shutdown
    validation_node.destroy_node()
    rclpy.shutdown()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()