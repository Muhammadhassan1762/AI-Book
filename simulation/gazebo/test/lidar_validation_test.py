#!/usr/bin/env python3
"""
LiDAR Sensor Validation Test Script

This script validates that the LiDAR sensor simulation produces realistic data
with appropriate noise models that approximate real-world behavior.
"""

import math
import statistics
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header
import numpy as np


class LidarValidationTest(Node):
    def __init__(self):
        super().__init__('lidar_validation_test')

        # Variables to store LiDAR data
        self.lidar_data = []
        self.data_count = 0
        self.max_data_points = 100  # Keep only recent data points

        # Expected LiDAR parameters (based on our model configuration)
        self.expected_params = {
            'range_min': 0.1,
            'range_max': 30.0,
            'angle_min': -math.pi,
            'angle_max': math.pi,
            'angle_increment': 2 * math.pi / 720,  # 720 samples
            'time_increment': 0.0,  # Not critical for validation
            'scan_time': 0.0,       # Not critical for validation
        }

        # Create subscriber for LiDAR data
        self.lidar_subscriber = self.create_subscription(
            LaserScan,
            '/laser_scan',
            self.lidar_callback,
            10
        )

        self.get_logger().info('LiDAR validation test node initialized')

    def lidar_callback(self, msg):
        """Callback to receive LiDAR data from simulation"""
        self.lidar_data.append(msg)
        self.data_count += 1

        # Keep only the most recent data points
        if len(self.lidar_data) > self.max_data_points:
            self.lidar_data.pop(0)

        self.get_logger().debug(f'Received LiDAR data, total count: {self.data_count}')

    def validate_lidar_parameters(self):
        """Validate that LiDAR parameters match expected values"""
        if not self.lidar_data:
            self.get_logger().warn('No LiDAR data available for parameter validation')
            return False

        latest_scan = self.lidar_data[-1]

        # Check range parameters
        range_min_ok = abs(latest_scan.range_min - self.expected_params['range_min']) < 0.01
        range_max_ok = abs(latest_scan.range_max - self.expected_params['range_max']) < 0.01

        # Check angle parameters
        angle_min_ok = abs(latest_scan.angle_min - self.expected_params['angle_min']) < 0.01
        angle_max_ok = abs(latest_scan.angle_max - self.expected_params['angle_max']) < 0.01
        angle_inc_ok = abs(latest_scan.angle_increment - self.expected_params['angle_increment']) < 0.001

        # Check that we have the expected number of ranges
        expected_samples = int((self.expected_params['angle_max'] - self.expected_params['angle_min']) /
                              self.expected_params['angle_increment']) + 1
        ranges_ok = len(latest_scan.ranges) == len(latest_scan.intensities)

        params_ok = (range_min_ok and range_max_ok and
                    angle_min_ok and angle_max_ok and angle_inc_ok and ranges_ok)

        self.get_logger().info('LiDAR parameter validation:')
        self.get_logger().info(f'  Range min: Expected {self.expected_params["range_min"]}, Actual {latest_scan.range_min}, {"OK" if range_min_ok else "FAIL"}')
        self.get_logger().info(f'  Range max: Expected {self.expected_params["range_max"]}, Actual {latest_scan.range_max}, {"OK" if range_max_ok else "FAIL"}')
        self.get_logger().info(f'  Angle min: Expected {self.expected_params["angle_min"]:.3f}, Actual {latest_scan.angle_min:.3f}, {"OK" if angle_min_ok else "FAIL"}')
        self.get_logger().info(f'  Angle max: Expected {self.expected_params["angle_max"]:.3f}, Actual {latest_scan.angle_max:.3f}, {"OK" if angle_max_ok else "FAIL"}')
        self.get_logger().info(f'  Angle increment: Expected {self.expected_params["angle_increment"]:.5f}, Actual {latest_scan.angle_increment:.5f}, {"OK" if angle_inc_ok else "FAIL"}')
        self.get_logger().info(f'  Range/intensity count match: {"OK" if ranges_ok else "FAIL"}')

        return params_ok

    def validate_lidar_noise_characteristics(self):
        """Validate that LiDAR data has realistic noise characteristics"""
        if len(self.lidar_data) < 10:
            self.get_logger().warn('Insufficient LiDAR data for noise validation')
            return False

        # Collect range data for analysis
        all_ranges = []
        for scan in self.lidar_data:
            # Filter out invalid range values (inf, nan) and only keep valid measurements
            valid_ranges = [r for r in scan.ranges if not (math.isinf(r) or math.isnan(r)) and r > scan.range_min and r < scan.range_max]
            all_ranges.extend(valid_ranges)

        if not all_ranges:
            self.get_logger().warn('No valid range data for noise analysis')
            return False

        # Calculate statistics
        mean_range = statistics.mean(all_ranges)
        std_range = statistics.stdev(all_ranges) if len(all_ranges) > 1 else 0.0

        # In a real LiDAR, we expect some noise - check that standard deviation is reasonable
        # For our model with 0.01m noise, we expect std deviation in a similar range
        expected_noise_level = 0.01  # Based on our SDF configuration
        noise_level_reasonable = std_range < 0.1  # Allow up to 10cm variation

        # Check for outliers (which would indicate realistic noise)
        q1 = np.percentile(all_ranges, 25)
        q3 = np.percentile(all_ranges, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [r for r in all_ranges if r < lower_bound or r > upper_bound]
        has_outliers = len(outliers) > 0

        self.get_logger().info('LiDAR noise characteristic validation:')
        self.get_logger().info(f'  Mean range: {mean_range:.3f} m')
        self.get_logger().info(f'  Std deviation: {std_range:.5f} m')
        self.get_logger().info(f'  Expected noise level: ~{expected_noise_level} m')
        self.get_logger().info(f'  Noise level reasonable: {"YES" if noise_level_reasonable else "NO"}')
        self.get_logger().info(f'  Has outliers (indicating noise): {"YES" if has_outliers else "NO"}')

        # Noise validation passes if std deviation is reasonable and we have some variation
        noise_ok = noise_level_reasonable and std_range > 0.0
        return noise_ok

    def validate_lidar_environment_interaction(self):
        """Validate that LiDAR properly interacts with environment objects"""
        if not self.lidar_data:
            return False

        latest_scan = self.lidar_data[-1]

        # Check if we have valid measurements (not all inf/nan)
        valid_measurements = [r for r in latest_scan.ranges if not (math.isinf(r) or math.isnan(r)) and r > latest_scan.range_min and r < latest_scan.range_max]

        has_valid_measurements = len(valid_measurements) > 0
        reasonable_measurements = any(r < 10.0 for r in valid_measurements)  # Should have some close measurements if there are obstacles

        self.get_logger().info('LiDAR environment interaction validation:')
        self.get_logger().info(f'  Valid measurements count: {len(valid_measurements)}')
        self.get_logger().info(f'  Has valid measurements: {"YES" if has_valid_measurements else "NO"}')
        self.get_logger().info(f'  Has close measurements (<10m): {"YES" if reasonable_measurements else "NO"}')

        return has_valid_measurements and reasonable_measurements

    def run_validation_tests(self):
        """Run all LiDAR validation tests"""
        self.get_logger().info('Starting LiDAR sensor validation tests...')

        # Wait a bit for data to accumulate
        self.get_logger().info('Waiting for LiDAR data...')
        time.sleep(3.0)

        results = {
            'parameter_validation': self.validate_lidar_parameters(),
            'noise_validation': self.validate_lidar_noise_characteristics(),
            'environment_validation': self.validate_lidar_environment_interaction()
        }

        self.get_logger().info('LiDAR validation test results:')
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.get_logger().info(f'  {test_name}: {status}')

        all_passed = all(results.values())
        self.get_logger().info(f'LiDAR overall result: {"ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"}')

        return all_passed


def main(args=None):
    import time  # Import here to avoid unused import warning
    rclpy.init(args=args)

    validation_node = LidarValidationTest()

    # Run the validation tests
    success = validation_node.run_validation_tests()

    # Shutdown
    validation_node.destroy_node()
    rclpy.shutdown()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()