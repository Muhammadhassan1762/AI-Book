#!/usr/bin/env python3
"""
Sensor Output Validation Script

This script validates that all sensor outputs approximate real-world behavior
by comparing simulation data to expected real-world sensor characteristics.
"""

import math
import statistics
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, Imu
from geometry_msgs.msg import Vector3
from std_msgs.msg import Header
from cv_bridge import CvBridge
import numpy as np


class SensorOutputValidation(Node):
    def __init__(self):
        super().__init__('sensor_output_validation')

        # Variables to store sensor data
        self.lidar_data = []
        self.camera_data = []
        self.imu_data = []

        self.max_data_points = 50

        # Create subscribers for all sensor data
        self.lidar_subscriber = self.create_subscription(
            LaserScan,
            '/laser_scan',
            self.lidar_callback,
            10
        )

        self.camera_subscriber = self.create_subscription(
            Image,
            '/depth_camera/image_raw',
            self.camera_callback,
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

        self.get_logger().info('Sensor output validation node initialized')

    def lidar_callback(self, msg):
        """Callback to receive LiDAR data from simulation"""
        self.lidar_data.append(msg)
        if len(self.lidar_data) > self.max_data_points:
            self.lidar_data.pop(0)

    def camera_callback(self, msg):
        """Callback to receive camera data from simulation"""
        self.camera_data.append(msg)
        if len(self.camera_data) > self.max_data_points:
            self.camera_data.pop(0)

    def imu_callback(self, msg):
        """Callback to receive IMU data from simulation"""
        self.imu_data.append(msg)
        if len(self.imu_data) > self.max_data_points:
            self.imu_data.pop(0)

    def validate_lidar_realism(self):
        """Validate that LiDAR output approximates real-world LiDAR behavior"""
        if len(self.lidar_data) < 10:
            self.get_logger().warn('Insufficient LiDAR data for realism validation')
            return False

        latest_scan = self.lidar_data[-1]

        # Check for realistic range values
        valid_ranges = [r for r in latest_scan.ranges
                       if not (math.isinf(r) or math.isnan(r))
                       and latest_scan.range_min <= r <= latest_scan.range_max]

        if not valid_ranges:
            self.get_logger().warn('No valid range measurements in LiDAR data')
            return False

        # Check that we have reasonable distribution of measurements
        # In a real environment, we should have a mix of close and far measurements
        close_measurements = [r for r in valid_ranges if r < 2.0]  # Within 2m
        far_measurements = [r for r in valid_ranges if r > 10.0]   # Beyond 10m

        has_variety = len(close_measurements) > 0 or len(far_measurements) > 0

        # Check for realistic measurement patterns (objects should create consistent returns)
        mean_range = statistics.mean(valid_ranges) if valid_ranges else 0
        std_range = statistics.stdev(valid_ranges) if len(valid_ranges) > 1 else 0

        # Real LiDAR typically has some clustering of similar measurements
        reasonable_clustering = std_range / (mean_range + 0.001) < 0.5  # Coefficient of variation

        self.get_logger().info('LiDAR realism validation:')
        self.get_logger().info(f'  Valid measurements: {len(valid_ranges)}')
        self.get_logger().info(f'  Has measurement variety: {"YES" if has_variety else "NO"}')
        self.get_logger().info(f'  Mean range: {mean_range:.3f} m')
        self.get_logger().info(f'  Std dev: {std_range:.3f} m')
        self.get_logger().info(f'  Reasonable clustering: {"YES" if reasonable_clustering else "NO"}')

        return has_variety and reasonable_clustering

    def validate_camera_realism(self):
        """Validate that camera output approximates real-world camera behavior"""
        if len(self.camera_data) < 3:
            self.get_logger().warn('Insufficient camera data for realism validation')
            return False

        try:
            latest_image = self.camera_data[-1]

            # Convert to OpenCV image for analysis
            cv_image = self.cv_bridge.imgmsg_to_cv2(latest_image, desired_encoding='passthrough')

            # Check image properties
            height, width = cv_image.shape[:2]
            has_reasonable_size = height >= 100 and width >= 100  # Minimum reasonable size

            # Check for realistic image content (not all zeros or all same values)
            unique_values = len(np.unique(cv_image))
            has_detail = unique_values > 10  # Should have more than just a few unique values

            # Calculate image statistics
            mean_intensity = float(np.mean(cv_image))
            std_intensity = float(np.std(cv_image))

            has_variation = std_intensity > 0.0

            self.get_logger().info('Camera realism validation:')
            self.get_logger().info(f'  Image size: {width}x{height}, {"OK" if has_reasonable_size else "FAIL"}')
            self.get_logger().info(f'  Unique pixel values: {unique_values}, {"OK" if has_detail else "FAIL"}')
            self.get_logger().info(f'  Has intensity variation: {"YES" if has_variation else "NO"}')

            return has_reasonable_size and has_detail and has_variation

        except Exception as e:
            self.get_logger().warn(f'Could not analyze camera image: {e}')
            return False

    def validate_imu_realism(self):
        """Validate that IMU output approximates real-world IMU behavior"""
        if len(self.imu_data) < 20:
            self.get_logger().warn('Insufficient IMU data for realism validation')
            return False

        # Collect IMU data
        acc_x = [msg.linear_acceleration.x for msg in self.imu_data]
        acc_y = [msg.linear_acceleration.y for msg in self.imu_data]
        acc_z = [msg.linear_acceleration.z for msg in self.imu_data]

        gyro_x = [msg.angular_velocity.x for msg in self.imu_data]
        gyro_y = [msg.angular_velocity.y for msg in self.imu_data]
        gyro_z = [msg.angular_velocity.z for msg in self.imu_data]

        # Check for realistic acceleration patterns
        # When robot is mostly stationary, acceleration should be dominated by gravity
        mean_acc_z = statistics.mean(acc_z)
        gravity_like = abs(abs(mean_acc_z) - 9.81) < 3.0  # Allow for robot movement

        # Check for realistic gyro patterns (should have some variation when robot moves)
        std_gyro_x = statistics.stdev(gyro_x) if len(set(gyro_x)) > 1 else 0.0
        std_gyro_y = statistics.stdev(gyro_y) if len(set(gyro_y)) > 1 else 0.0
        std_gyro_z = statistics.stdev(gyro_z) if len(set(gyro_z)) > 1 else 0.0

        has_rotation_variation = (std_gyro_x > 0.001 or
                                 std_gyro_y > 0.001 or
                                 std_gyro_z > 0.001)

        # Check that values are within reasonable ranges for IMU
        reasonable_acc_range = all(abs(acc) < 20.0 for acc in acc_x + acc_y + acc_z)  # Max 20 m/s²
        reasonable_gyro_range = all(abs(gyro) < 10.0 for gyro in gyro_x + gyro_y + gyro_z)  # Max 10 rad/s

        self.get_logger().info('IMU realism validation:')
        self.get_logger().info(f'  Mean Acc Z: {mean_acc_z:.3f} m/s² (gravity-like: {"YES" if gravity_like else "NO"})')
        self.get_logger().info(f'  Has rotation variation: {"YES" if has_rotation_variation else "NO"}')
        self.get_logger().info(f'  Reasonable acceleration range: {"YES" if reasonable_acc_range else "NO"}')
        self.get_logger().info(f'  Reasonable gyro range: {"YES" if reasonable_gyro_range else "NO"}')

        return (gravity_like or reasonable_acc_range) and has_rotation_variation and reasonable_gyro_range

    def validate_sensor_consistency(self):
        """Validate that sensors provide consistent information about the environment"""
        # This would check for consistency between different sensor modalities
        # For example, IMU orientation should be consistent with LiDAR measurements over time
        # For now, we'll just verify that all sensors are publishing data

        lidar_active = len(self.lidar_data) > 0
        camera_active = len(self.camera_data) > 0
        imu_active = len(self.imu_data) > 0

        all_active = lidar_active and camera_active and imu_active

        self.get_logger().info('Sensor consistency validation:')
        self.get_logger().info(f'  LiDAR active: {"YES" if lidar_active else "NO"}')
        self.get_logger().info(f'  Camera active: {"YES" if camera_active else "NO"}')
        self.get_logger().info(f'  IMU active: {"YES" if imu_active else "NO"}')
        self.get_logger().info(f'  All sensors active: {"YES" if all_active else "NO"}')

        return all_active

    def run_validation_tests(self):
        """Run all sensor output validation tests"""
        self.get_logger().info('Starting comprehensive sensor output validation...')

        # Wait a bit for data to accumulate
        self.get_logger().info('Waiting for sensor data...')
        time.sleep(5.0)

        results = {
            'lidar_realism': self.validate_lidar_realism(),
            'camera_realism': self.validate_camera_realism(),
            'imu_realism': self.validate_imu_realism(),
            'sensor_consistency': self.validate_sensor_consistency()
        }

        self.get_logger().info('Sensor output validation results:')
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.get_logger().info(f'  {test_name}: {status}')

        all_passed = all(results.values())
        self.get_logger().info(f'Sensor output overall result: {"ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"}')

        return all_passed


def main(args=None):
    import time  # Import here to avoid unused import warning
    rclpy.init(args=args)

    validation_node = SensorOutputValidation()

    # Run the validation tests
    success = validation_node.run_validation_tests()

    # Shutdown
    validation_node.destroy_node()
    rclpy.shutdown()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()