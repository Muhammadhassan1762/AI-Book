#!/usr/bin/env python3
"""
Depth Camera and IMU Sensor Validation Test Script

This script validates that the depth camera and IMU sensor simulations
produce realistic data with appropriate noise models.
"""

import math
import statistics
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from std_msgs.msg import Header
from cv_bridge import CvBridge
import numpy as np


class CameraIMUValidationTest(Node):
    def __init__(self):
        super().__init__('camera_imu_validation_test')

        # Variables to store sensor data
        self.depth_camera_data = []
        self.imu_data = []
        self.data_count = 0
        self.max_data_points = 50  # Keep only recent data points

        # Create subscribers for sensor data
        self.depth_camera_subscriber = self.create_subscription(
            Image,
            '/depth_camera/image_raw',
            self.depth_camera_callback,
            10
        )

        self.imu_subscriber = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        # Initialize CV bridge for image processing
        self.cv_bridge = CvBridge()

        self.get_logger().info('Camera and IMU validation test node initialized')

    def depth_camera_callback(self, msg):
        """Callback to receive depth camera data from simulation"""
        self.depth_camera_data.append(msg)
        self.data_count += 1

        # Keep only the most recent data points
        if len(self.depth_camera_data) > self.max_data_points:
            self.depth_camera_data.pop(0)

        self.get_logger().debug(f'Received depth camera data, total count: {self.data_count}')

    def imu_callback(self, msg):
        """Callback to receive IMU data from simulation"""
        self.imu_data.append(msg)
        self.data_count += 1

        # Keep only the most recent data points
        if len(self.imu_data) > self.max_data_points:
            self.imu_data.pop(0)

        self.get_logger().debug(f'Received IMU data, total count: {self.data_count}')

    def validate_depth_camera_parameters(self):
        """Validate that depth camera parameters are reasonable"""
        if not self.depth_camera_data:
            self.get_logger().warn('No depth camera data available for validation')
            return False

        latest_image = self.depth_camera_data[-1]

        # Check image parameters
        width_ok = latest_image.width > 0
        height_ok = latest_image.height > 0
        encoding_ok = latest_image.encoding in ['rgb8', 'bgr8', 'mono8', 'mono16']

        params_ok = width_ok and height_ok and encoding_ok

        self.get_logger().info('Depth camera parameter validation:')
        self.get_logger().info(f'  Width: {latest_image.width}, Height: {latest_image.height}, {"OK" if width_ok and height_ok else "FAIL"}')
        self.get_logger().info(f'  Encoding: {latest_image.encoding}, {"OK" if encoding_ok else "FAIL"}')

        return params_ok

    def validate_depth_camera_noise(self):
        """Validate that depth camera has realistic noise characteristics"""
        if len(self.depth_camera_data) < 5:
            self.get_logger().warn('Insufficient depth camera data for noise validation')
            return False

        try:
            # Convert image to numpy array for analysis
            latest_image = self.depth_camera_data[-1]
            cv_image = self.cv_bridge.imgmsg_to_cv2(latest_image, desired_encoding='passthrough')

            # Calculate image statistics
            mean_intensity = float(np.mean(cv_image))
            std_intensity = float(np.std(cv_image))

            # For a realistic image, we expect some variation (noise)
            has_variation = std_intensity > 0.0
            reasonable_intensity = 0 <= mean_intensity <= 255  # For 8-bit images

            self.get_logger().info('Depth camera noise validation:')
            self.get_logger().info(f'  Mean intensity: {mean_intensity:.2f}')
            self.get_logger().info(f'  Std intensity: {std_intensity:.2f}')
            self.get_logger().info(f'  Has variation: {"YES" if has_variation else "NO"}')
            self.get_logger().info(f'  Reasonable intensity: {"YES" if reasonable_intensity else "NO"}')

            return has_variation and reasonable_intensity

        except Exception as e:
            self.get_logger().warn(f'Could not analyze depth camera image: {e}')
            return False

    def validate_imu_parameters(self):
        """Validate that IMU parameters are reasonable"""
        if not self.imu_data:
            self.get_logger().warn('No IMU data available for validation')
            return False

        latest_imu = self.imu_data[-1]

        # Check that orientation, angular velocity, and linear acceleration are present
        orientation_ok = latest_imu.orientation.x is not None
        angular_vel_ok = latest_imu.angular_velocity.x is not None
        linear_acc_ok = latest_imu.linear_acceleration.x is not None

        params_ok = orientation_ok and angular_vel_ok and linear_acc_ok

        self.get_logger().info('IMU parameter validation:')
        self.get_logger().info(f'  Orientation present: {"YES" if orientation_ok else "NO"}')
        self.get_logger().info(f'  Angular velocity present: {"YES" if angular_vel_ok else "NO"}')
        self.get_logger().info(f'  Linear acceleration present: {"YES" if linear_acc_ok else "NO"}')

        return params_ok

    def validate_imu_gravity_detection(self):
        """Validate that IMU properly detects gravity in static conditions"""
        if len(self.imu_data) < 10:
            self.get_logger().warn('Insufficient IMU data for gravity validation')
            return False

        # Collect linear acceleration data
        acc_x = [msg.linear_acceleration.x for msg in self.imu_data]
        acc_y = [msg.linear_acceleration.y for msg in self.imu_data]
        acc_z = [msg.linear_acceleration.z for msg in self.imu_data]

        # Calculate mean values (should be close to expected gravity in z-axis when robot is upright)
        mean_acc_x = statistics.mean(acc_x)
        mean_acc_y = statistics.mean(acc_y)
        mean_acc_z = statistics.mean(acc_z)

        # When robot is upright and stationary, z-axis should show ~9.81 m/s² (gravity)
        # x and y should be close to 0
        x_near_zero = abs(mean_acc_x) < 1.0
        y_near_zero = abs(mean_acc_y) < 1.0
        z_near_gravity = abs(abs(mean_acc_z) - 9.81) < 2.0  # Allow for some variation

        gravity_detected = x_near_zero and y_near_zero and z_near_gravity

        self.get_logger().info('IMU gravity detection validation:')
        self.get_logger().info(f'  Mean Acc X: {mean_acc_x:.3f} m/s² (should be ~0), {"OK" if x_near_zero else "FAIL"}')
        self.get_logger().info(f'  Mean Acc Y: {mean_acc_y:.3f} m/s² (should be ~0), {"OK" if y_near_zero else "FAIL"}')
        self.get_logger().info(f'  Mean Acc Z: {mean_acc_z:.3f} m/s² (should be ~±9.81), {"OK" if z_near_gravity else "FAIL"}')
        self.get_logger().info(f'  Gravity properly detected: {"YES" if gravity_detected else "NO"}')

        return gravity_detected

    def validate_imu_noise_characteristics(self):
        """Validate that IMU has realistic noise characteristics"""
        if len(self.imu_data) < 20:
            self.get_logger().warn('Insufficient IMU data for noise validation')
            return False

        # Collect angular velocity data to analyze noise
        ang_vel_x = [msg.angular_velocity.x for msg in self.imu_data]
        ang_vel_y = [msg.angular_velocity.y for msg in self.imu_data]
        ang_vel_z = [msg.angular_velocity.z for msg in self.imu_data]

        # Calculate standard deviations
        std_x = statistics.stdev(ang_vel_x) if len(set(ang_vel_x)) > 1 else 0.0
        std_y = statistics.stdev(ang_vel_y) if len(set(ang_vel_y)) > 1 else 0.0
        std_z = statistics.stdev(ang_vel_z) if len(set(ang_vel_z)) > 1 else 0.0

        # For a realistic IMU simulation, we expect some noise
        has_noise = std_x > 0.0 or std_y > 0.0 or std_z > 0.0
        reasonable_noise = (std_x < 0.1 and std_y < 0.1 and std_z < 0.1)  # Reasonable noise levels

        self.get_logger().info('IMU noise characteristic validation:')
        self.get_logger().info(f'  Angular velocity std X: {std_x:.6f}')
        self.get_logger().info(f'  Angular velocity std Y: {std_y:.6f}')
        self.get_logger().info(f'  Angular velocity std Z: {std_z:.6f}')
        self.get_logger().info(f'  Has noise: {"YES" if has_noise else "NO"}')
        self.get_logger().info(f'  Reasonable noise levels: {"YES" if reasonable_noise else "NO"}')

        return has_noise and reasonable_noise

    def run_validation_tests(self):
        """Run all camera and IMU validation tests"""
        self.get_logger().info('Starting depth camera and IMU sensor validation tests...')

        # Wait a bit for data to accumulate
        self.get_logger().info('Waiting for sensor data...')
        time.sleep(3.0)

        results = {
            'camera_params': self.validate_depth_camera_parameters(),
            'camera_noise': self.validate_depth_camera_noise(),
            'imu_params': self.validate_imu_parameters(),
            'imu_gravity': self.validate_imu_gravity_detection(),
            'imu_noise': self.validate_imu_noise_characteristics()
        }

        self.get_logger().info('Camera and IMU validation test results:')
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.get_logger().info(f'  {test_name}: {status}')

        all_passed = all(results.values())
        self.get_logger().info(f'Camera and IMU overall result: {"ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"}')

        return all_passed


def main(args=None):
    import time  # Import here to avoid unused import warning
    rclpy.init(args=args)

    validation_node = CameraIMUValidationTest()

    # Run the validation tests
    success = validation_node.run_validation_tests()

    # Shutdown
    validation_node.destroy_node()
    rclpy.shutdown()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()