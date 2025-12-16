#!/usr/bin/env python3
"""
Map Generator Node

This ROS 2 node generates occupancy grid maps from pose estimates and sensor data
for use in navigation systems.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import LaserScan, Image
from nav_msgs.msg import OccupancyGrid, MapMetaData
from geometry_msgs.msg import Point
from std_msgs.msg import Header
from tf2_ros import TransformListener, Buffer
import tf2_geometry_msgs
import numpy as np
from scipy.ndimage import binary_dilation
import math


class MapGenerator(Node):
    def __init__(self):
        super().__init__('map_generator')

        # Declare parameters
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('resolution', 0.05)
        self.declare_parameter('width', 40.0)  # meters
        self.declare_parameter('height', 40.0)  # meters
        self.declare_parameter('origin_x', -20.0)
        self.declare_parameter('origin_y', -20.0)
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('update_rate', 5.0)
        self.declare_parameter('laser_topic', '/scan')
        self.declare_parameter('max_range', 10.0)
        self.declare_parameter('free_threshold', 0.2)
        self.declare_parameter('occupied_threshold', 0.65)

        # Get parameters
        self.map_frame = self.get_parameter('map_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.resolution = self.get_parameter('resolution').value
        self.width = self.get_parameter('width').value
        self.height = self.get_parameter('height').value
        self.origin_x = self.get_parameter('origin_x').value
        self.origin_y = self.get_parameter('origin_y').value
        self.publish_rate = self.get_parameter('publish_rate').value
        self.update_rate = self.get_parameter('update_rate').value
        self.laser_topic = self.get_parameter('laser_topic').value
        self.max_range = self.get_parameter('max_range').value
        self.free_threshold = self.get_parameter('free_threshold').value
        self.occupied_threshold = self.get_parameter('occupied_threshold').value

        # Calculate map dimensions
        self.map_width = int(self.width / self.resolution)
        self.map_height = int(self.height / self.resolution)

        # Initialize map data (probabilities)
        self.map_data = np.full((self.map_height, self.map_width), -1, dtype=np.int8)  # -1 = unknown

        # Initialize TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # QoS profile
        qos_profile = QoSProfile(depth=10)

        # Create subscribers
        self.laser_sub = self.create_subscription(
            LaserScan,
            self.laser_topic,
            self.laser_callback,
            qos_profile
        )

        # Create publishers
        self.map_pub = self.create_publisher(OccupancyGrid, '/vslam/map', qos_profile)

        # Create timers
        self.map_timer = self.create_timer(1.0/self.publish_rate, self.publish_map)

        # Initialize map metadata
        self.map_metadata = MapMetaData()
        self.map_metadata.resolution = self.resolution
        self.map_metadata.width = self.map_width
        self.map_metadata.height = self.map_height
        self.map_metadata.origin.position.x = self.origin_x
        self.map_metadata.origin.position.y = self.origin_y
        self.map_metadata.origin.position.z = 0.0
        self.map_metadata.origin.orientation.x = 0.0
        self.map_metadata.origin.orientation.y = 0.0
        self.map_metadata.origin.orientation.z = 0.0
        self.map_metadata.origin.orientation.w = 1.0

        self.get_logger().info(f'Map Generator node initialized with {self.map_width}x{self.map_height} map')

    def laser_callback(self, msg):
        """Process laser scan data to update the map"""
        try:
            # Get robot's current pose in map frame
            try:
                transform = self.tf_buffer.lookup_transform(
                    self.map_frame,
                    self.base_frame,
                    rclpy.time.Time(),
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )

                robot_x = transform.transform.translation.x
                robot_y = transform.transform.translation.y
                robot_yaw = self.quaternion_to_yaw(
                    transform.transform.rotation.x,
                    transform.transform.rotation.y,
                    transform.transform.rotation.z,
                    transform.transform.rotation.w
                )
            except Exception as e:
                self.get_logger().warn(f'Could not get transform: {e}')
                return

            # Convert robot pose to map coordinates
            robot_map_x = int((robot_x - self.origin_x) / self.resolution)
            robot_map_y = int((robot_y - self.origin_y) / self.resolution)

            # Check if robot is within map bounds
            if not (0 <= robot_map_x < self.map_width and 0 <= robot_map_y < self.map_height):
                self.get_logger().warn('Robot pose is outside map bounds')
                return

            # Process laser scan data
            angle_increment = msg.angle_increment
            current_angle = msg.angle_min

            for i, range_reading in enumerate(msg.ranges):
                if not (np.isfinite(range_reading) and msg.range_min <= range_reading <= msg.range_max):
                    current_angle += angle_increment
                    continue

                # Calculate point in laser frame
                laser_x = range_reading * math.cos(current_angle)
                laser_y = range_reading * math.sin(current_angle)

                # Transform to base frame
                base_x = laser_x * math.cos(robot_yaw) - laser_y * math.sin(robot_yaw) + robot_x
                base_y = laser_x * math.sin(robot_yaw) + laser_y * math.cos(robot_yaw) + robot_y

                # Convert to map coordinates
                map_x = int((base_x - self.origin_x) / self.resolution)
                map_y = int((base_y - self.origin_y) / self.resolution)

                # Check bounds
                if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                    # Mark endpoint as occupied
                    self.map_data[map_y, map_x] = 100  # occupied

                    # Mark free space along the beam using Bresenham's algorithm
                    self.mark_free_space(robot_map_x, robot_map_y, map_x, map_y)

                current_angle += angle_increment

        except Exception as e:
            self.get_logger().error(f'Error processing laser scan: {e}')

    def mark_free_space(self, x0, y0, x1, y1):
        """Mark free space along a line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            # Check bounds
            if 0 <= x < self.map_width and 0 <= y < self.map_height:
                # Only mark as free if not already occupied
                if self.map_data[y, x] != 100:
                    self.map_data[y, x] = 0  # free space

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def publish_map(self):
        """Publish the occupancy grid map"""
        try:
            # Create OccupancyGrid message
            map_msg = OccupancyGrid()
            map_msg.header = Header()
            map_msg.header.stamp = self.get_clock().now().to_msg()
            map_msg.header.frame_id = self.map_frame
            map_msg.info = self.map_metadata

            # Flatten map data for message
            flat_data = self.map_data.flatten()
            map_msg.data = flat_data.tolist()

            # Publish map
            self.map_pub.publish(map_msg)

            self.get_logger().debug(f'Published map with {len(map_msg.data)} cells')

        except Exception as e:
            self.get_logger().error(f'Error publishing map: {e}')

    def quaternion_to_yaw(self, x, y, z, w):
        """Convert quaternion to yaw angle"""
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        return math.atan2(siny_cosp, cosy_cosp)

    def reset_map(self):
        """Reset the map to unknown state"""
        self.map_data = np.full((self.map_height, self.map_width), -1, dtype=np.int8)
        self.get_logger().info('Map reset to unknown state')


def main(args=None):
    rclpy.init(args=args)

    node = MapGenerator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()