#!/usr/bin/env python3
"""
Synthetic Data Generator Node

This ROS 2 node interfaces with Isaac Sim Replicator to generate synthetic datasets
containing RGB, Depth, and Segmentation images for robotics perception training.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import String, Bool
from sensor_msgs.msg import Image
import cv2
import numpy as np
import yaml
import os
from pathlib import Path


class SyntheticDataGenerator(Node):
    def __init__(self):
        super().__init__('synthetic_data_generator')

        # Declare parameters
        self.declare_parameter('dataset_type', 'all')
        self.declare_parameter('output_path', '/workspace/datasets')
        self.declare_parameter('num_samples', 1000)
        self.declare_parameter('enable_rgb', True)
        self.declare_parameter('enable_depth', True)
        self.declare_parameter('enable_segmentation', True)
        self.declare_parameter('scene_path', '')
        self.declare_parameter('config_path', '')

        # Get parameters
        self.dataset_type = self.get_parameter('dataset_type').value
        self.output_path = self.get_parameter('output_path').value
        self.num_samples = self.get_parameter('num_samples').value
        self.enable_rgb = self.get_parameter('enable_rgb').value
        self.enable_depth = self.get_parameter('enable_depth').value
        self.enable_segmentation = self.get_parameter('enable_segmentation').value
        self.scene_path = self.get_parameter('scene_path').value
        self.config_path = self.get_parameter('config_path').value

        # Validate parameters
        if self.dataset_type not in ['rgb', 'depth', 'segmentation', 'all']:
            self.get_logger().error(f"Invalid dataset_type: {self.dataset_type}")
            self.dataset_type = 'all'

        # Create output directories
        self.create_output_directories()

        # Publishers for status updates
        self.status_pub = self.create_publisher(String, 'synthetic_data/status', 10)
        self.progress_pub = self.create_publisher(String, 'synthetic_data/progress', 10)

        # Subscribers for control
        self.start_sub = self.create_subscription(
            Bool,
            'synthetic_data/start_generation',
            self.start_generation_callback,
            10
        )

        # Service clients for Isaac Sim interaction
        # In a real implementation, these would connect to Isaac Sim services
        self.get_logger().info('Synthetic Data Generator node initialized')
        self.get_logger().info(f'Configuration: dataset_type={self.dataset_type}, '
                              f'output_path={self.output_path}, num_samples={self.num_samples}')

    def create_output_directories(self):
        """Create necessary output directories"""
        try:
            if self.enable_rgb or self.dataset_type in ['rgb', 'all']:
                rgb_path = os.path.join(self.output_path, 'rgb')
                os.makedirs(rgb_path, exist_ok=True)
                self.get_logger().info(f'Created RGB output directory: {rgb_path}')

            if self.enable_depth or self.dataset_type in ['depth', 'all']:
                depth_path = os.path.join(self.output_path, 'depth')
                os.makedirs(depth_path, exist_ok=True)
                self.get_logger().info(f'Created Depth output directory: {depth_path}')

            if self.enable_segmentation or self.dataset_type in ['segmentation', 'all']:
                seg_path = os.path.join(self.output_path, 'segmentation')
                os.makedirs(seg_path, exist_ok=True)
                self.get_logger().info(f'Created Segmentation output directory: {seg_path}')

        except Exception as e:
            self.get_logger().error(f'Failed to create output directories: {e}')

    def start_generation_callback(self, msg):
        """Start the synthetic data generation process"""
        if msg.data:
            self.get_logger().info('Starting synthetic data generation...')
            self.publish_status('Starting generation')
            self.generate_dataset()
        else:
            self.get_logger().info('Stopping synthetic data generation...')
            self.publish_status('Generation stopped')

    def generate_dataset(self):
        """Main dataset generation function"""
        try:
            # Load configuration
            config = self.load_config()
            if config is None:
                self.get_logger().error('Failed to load configuration')
                return

            # Initialize Isaac Sim connection
            # In a real implementation, this would connect to Isaac Sim
            self.get_logger().info('Initializing Isaac Sim connection...')

            # Generate samples
            for i in range(self.num_samples):
                # Publish progress
                progress_msg = String()
                progress_msg.data = f'Generating sample {i+1}/{self.num_samples}'
                self.progress_pub.publish(progress_msg)

                # Generate RGB image (simulated)
                if self.enable_rgb or self.dataset_type in ['rgb', 'all']:
                    self.generate_rgb_image(i)

                # Generate depth image (simulated)
                if self.enable_depth or self.dataset_type in ['depth', 'all']:
                    self.generate_depth_image(i)

                # Generate segmentation image (simulated)
                if self.enable_segmentation or self.dataset_type in ['segmentation', 'all']:
                    self.generate_segmentation_image(i)

                # Log progress every 100 samples
                if (i + 1) % 100 == 0:
                    self.get_logger().info(f'Generated {i+1}/{self.num_samples} samples')

            # Complete generation
            self.get_logger().info('Dataset generation completed successfully')
            self.publish_status('Generation completed')

        except Exception as e:
            self.get_logger().error(f'Error during dataset generation: {e}')
            self.publish_status(f'Generation failed: {e}')

    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    self.get_logger().info(f'Loaded configuration from {self.config_path}')
                    return config
            else:
                self.get_logger().warn(f'Config file not found: {self.config_path}')
                return None
        except Exception as e:
            self.get_logger().error(f'Error loading config: {e}')
            return None

    def generate_rgb_image(self, sample_id):
        """Generate a synthetic RGB image (simulated)"""
        try:
            # In a real implementation, this would capture from Isaac Sim
            # For simulation, we'll create a dummy RGB image
            height, width = 480, 640
            rgb_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

            # Add some structure to make it look more realistic
            cv2.circle(rgb_image, (width//2, height//2), 50, (255, 0, 0), -1)
            cv2.rectangle(rgb_image, (100, 100), (200, 200), (0, 255, 0), -1)

            # Save the image
            output_path = os.path.join(self.output_path, 'rgb', f'rgb_{sample_id:06d}.png')
            cv2.imwrite(output_path, cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))

        except Exception as e:
            self.get_logger().error(f'Error generating RGB image {sample_id}: {e}')

    def generate_depth_image(self, sample_id):
        """Generate a synthetic depth image (simulated)"""
        try:
            # In a real implementation, this would capture from Isaac Sim
            # For simulation, we'll create a dummy depth image
            height, width = 480, 640
            depth_image = np.random.uniform(0.1, 10.0, (height, width)).astype(np.float32)

            # Add some structure (depth increases with y coordinate)
            for y in range(height):
                depth_image[y, :] = depth_image[y, :] * (1 + y / height)

            # Save the image
            output_path = os.path.join(self.output_path, 'depth', f'depth_{sample_id:06d}.tiff')
            cv2.imwrite(output_path, (depth_image * 1000).astype(np.uint16))  # Convert to mm for 16-bit storage

        except Exception as e:
            self.get_logger().error(f'Error generating depth image {sample_id}: {e}')

    def generate_segmentation_image(self, sample_id):
        """Generate a synthetic segmentation image (simulated)"""
        try:
            # In a real implementation, this would capture from Isaac Sim
            # For simulation, we'll create a dummy segmentation image
            height, width = 480, 640
            seg_image = np.zeros((height, width), dtype=np.uint8)

            # Create different segments
            seg_image[100:200, 100:200] = 1  # Class 1
            seg_image[200:300, 200:300] = 2  # Class 2
            seg_image[300:400, 100:200] = 3  # Class 3
            seg_image[100:400, 300:500] = 4  # Class 4 (background)

            # Save the image
            output_path = os.path.join(self.output_path, 'segmentation', f'seg_{sample_id:06d}.png')
            cv2.imwrite(output_path, seg_image)

        except Exception as e:
            self.get_logger().error(f'Error generating segmentation image {sample_id}: {e}')

    def publish_status(self, status):
        """Publish status message"""
        status_msg = String()
        status_msg.data = status
        self.status_pub.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)

    node = SyntheticDataGenerator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()