#!/usr/bin/env python3
"""
VSLAM Processor Node

This ROS 2 node implements Visual Simultaneous Localization and Mapping (VSLAM)
functionality to process camera inputs and generate maps and pose estimates.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import OccupancyGrid, Path
from std_msgs.msg import Header
from cv_bridge import CvBridge
import cv2
import numpy as np
import tf2_ros
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import yaml
from scipy.spatial.transform import Rotation as R
import math


class VSLAMProcessor(Node):
    def __init__(self):
        super().__init__('vslam_processor')

        # Declare parameters
        self.declare_parameter('rgb_topic', '/camera/rgb/image_rect_color')
        self.declare_parameter('depth_topic', '/camera/depth/image_rect_raw')
        self.declare_parameter('enable_rectification', True)
        self.declare_parameter('enable_stereo', False)
        self.declare_parameter('enable_visualization', True)
        self.declare_parameter('enable_point_cloud', True)
        self.declare_parameter('max_features', 2000)
        self.declare_parameter('min_features', 100)
        self.declare_parameter('tracking_quality_threshold', 0.5)
        self.declare_parameter('min_keyframe_distance', 0.2)
        self.declare_parameter('enable_loop_closure', True)
        self.declare_parameter('publish_rate', 30.0)
        self.declare_parameter('map_publish_rate', 1.0)
        self.declare_parameter('pose_publish_rate', 30.0)
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('camera_frame', 'camera_link')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')

        # Get parameters
        self.rgb_topic = self.get_parameter('rgb_topic').value
        self.depth_topic = self.get_parameter('depth_topic').value
        self.enable_rectification = self.get_parameter('enable_rectification').value
        self.enable_stereo = self.get_parameter('enable_stereo').value
        self.enable_visualization = self.get_parameter('enable_visualization').value
        self.enable_point_cloud = self.get_parameter('enable_point_cloud').value
        self.max_features = self.get_parameter('max_features').value
        self.min_features = self.get_parameter('min_features').value
        self.tracking_quality_threshold = self.get_parameter('tracking_quality_threshold').value
        self.min_keyframe_distance = self.get_parameter('min_keyframe_distance').value
        self.enable_loop_closure = self.get_parameter('enable_loop_closure').value
        self.publish_rate = self.get_parameter('publish_rate').value
        self.map_publish_rate = self.get_parameter('map_publish_rate').value
        self.pose_publish_rate = self.get_parameter('pose_publish_rate').value
        self.base_frame = self.get_parameter('base_frame').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.map_frame = self.get_parameter('map_frame').value
        self.odom_frame = self.get_parameter('odom_frame').value

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Initialize feature detector (using ORB as an example)
        self.feature_detector = cv2.ORB_create(nfeatures=self.max_features)

        # Initialize map and pose tracking
        self.current_pose = np.eye(4)  # 4x4 transformation matrix
        self.keyframes = []
        self.map_points = []
        self.previous_features = None
        self.previous_image = None

        # QoS profile for sensor data
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Create subscribers
        self.rgb_sub = self.create_subscription(
            Image,
            self.rgb_topic,
            self.rgb_callback,
            sensor_qos
        )

        self.depth_sub = self.create_subscription(
            Image,
            self.depth_topic,
            self.depth_callback,
            sensor_qos
        )

        # Create publishers
        self.pose_pub = self.create_publisher(PoseStamped, '/vslam/pose', 10)
        self.map_pub = self.create_publisher(OccupancyGrid, '/vslam/map', 10)
        self.trajectory_pub = self.create_publisher(Path, '/vslam/trajectory', 10)

        # Create TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # Create timers
        self.pose_timer = self.create_timer(1.0/self.pose_publish_rate, self.publish_pose)
        self.map_timer = self.create_timer(1.0/self.map_publish_rate, self.publish_map)

        # Initialize pose for the path
        self.trajectory_poses = []

        self.get_logger().info('VSLAM Processor node initialized')

    def rgb_callback(self, msg):
        """Process RGB image for feature detection and tracking"""
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Detect features
            keypoints, descriptors = self.feature_detector.detectAndCompute(cv_image, None)

            if descriptors is not None and len(keypoints) >= self.min_features:
                # Convert keypoints to numpy array
                current_features = np.array([kp.pt for kp in keypoints], dtype=np.float32)

                # Track features if we have previous features
                if self.previous_features is not None and self.previous_image is not None:
                    # Calculate optical flow to track features
                    current_features_reshaped = current_features.reshape(-1, 1, 2)
                    previous_features_reshaped = self.previous_features.reshape(-1, 1, 2)

                    # Use Lucas-Kanade optical flow to track features
                    status, error = cv2.calcOpticalFlowPyrLK(
                        self.previous_image, cv_image,
                        previous_features_reshaped, current_features_reshaped
                    )

                    # Filter good points
                    good_new = current_features[status.ravel() == 1]
                    good_old = self.previous_features[status.ravel() == 1]

                    # Estimate motion using essential matrix if enough points
                    if len(good_new) >= 8:
                        # Estimate essential matrix
                        E, mask = cv2.findEssentialMat(
                            good_new, good_old,
                            cameraMatrix=np.array([[384, 0, 320], [0, 384, 240], [0, 0, 1]]),
                            method=cv2.RANSAC, prob=0.999, threshold=1.0
                        )

                        if E is not None:
                            # Recover pose from essential matrix
                            _, R, t, _ = cv2.recoverPose(E, good_new, good_old)

                            # Create transformation matrix
                            T = np.eye(4)
                            T[:3, :3] = R
                            T[:3, 3] = t.flatten() * 0.1  # Scale factor for demonstration

                            # Update current pose
                            self.current_pose = self.current_pose @ T

                            # Check if this should be a keyframe
                            translation_norm = np.linalg.norm(T[:3, 3])
                            if translation_norm > self.min_keyframe_distance:
                                self.keyframes.append((self.current_pose.copy(), cv_image.copy()))

                # Update previous features and image
                self.previous_features = current_features
                self.previous_image = cv_image.copy()

            # Store current pose in trajectory
            self.trajectory_poses.append(self.current_pose.copy())

        except Exception as e:
            self.get_logger().error(f'Error processing RGB image: {e}')

    def depth_callback(self, msg):
        """Process depth image for 3D reconstruction"""
        try:
            # Convert ROS image to OpenCV
            cv_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

            # Process depth data if needed
            # In a real implementation, this would be used for 3D point cloud generation
            pass

        except Exception as e:
            self.get_logger().error(f'Error processing depth image: {e}')

    def publish_pose(self):
        """Publish current estimated pose"""
        try:
            # Create PoseStamped message
            pose_msg = PoseStamped()
            pose_msg.header = Header()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = self.map_frame

            # Extract position and orientation from transformation matrix
            position = self.current_pose[:3, 3]
            rotation_matrix = self.current_pose[:3, :3]

            # Convert rotation matrix to quaternion
            r = R.from_matrix(rotation_matrix)
            quat = r.as_quat()

            pose_msg.pose.position.x = float(position[0])
            pose_msg.pose.position.y = float(position[1])
            pose_msg.pose.position.z = float(position[2])
            pose_msg.pose.orientation.x = float(quat[0])
            pose_msg.pose.orientation.y = float(quat[1])
            pose_msg.pose.orientation.z = float(quat[2])
            pose_msg.pose.orientation.w = float(quat[3])

            # Publish pose
            self.pose_pub.publish(pose_msg)

            # Broadcast transform
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = self.map_frame
            t.child_frame_id = self.base_frame
            t.transform.translation.x = float(position[0])
            t.transform.translation.y = float(position[1])
            t.transform.translation.z = float(position[2])
            t.transform.rotation.x = float(quat[0])
            t.transform.rotation.y = float(quat[1])
            t.transform.rotation.z = float(quat[2])
            t.transform.rotation.w = float(quat[3])

            self.tf_broadcaster.sendTransform(t)

        except Exception as e:
            self.get_logger().error(f'Error publishing pose: {e}')

    def publish_map(self):
        """Publish occupancy grid map"""
        try:
            # Create a simple occupancy grid for demonstration
            # In a real implementation, this would be generated from the VSLAM map
            map_msg = OccupancyGrid()
            map_msg.header = Header()
            map_msg.header.stamp = self.get_clock().now().to_msg()
            map_msg.header.frame_id = self.map_frame

            # Map parameters
            map_msg.info.resolution = 0.05  # 5cm per cell
            map_msg.info.width = 400  # 20m x 40 cells per meter
            map_msg.info.height = 400  # 20m x 40 cells per meter
            map_msg.info.origin.position.x = -10.0
            map_msg.info.origin.position.y = -10.0
            map_msg.info.origin.position.z = 0.0
            map_msg.info.origin.orientation.w = 1.0

            # Initialize map data (0 = free, 100 = occupied, -1 = unknown)
            map_data = [-1] * (map_msg.info.width * map_msg.info.height)

            # Add some obstacles based on trajectory (for demonstration)
            for pose in self.trajectory_poses[-50:]:  # Last 50 poses
                x = int((pose[0, 3] - map_msg.info.origin.position.x) / map_msg.info.resolution)
                y = int((pose[0, 3] - map_msg.info.origin.position.y) / map_msg.info.resolution)

                if 0 <= x < map_msg.info.width and 0 <= y < map_msg.info.height:
                    idx = y * map_msg.info.width + x
                    if 0 <= idx < len(map_data):
                        map_data[idx] = 0  # Mark as free space

            map_msg.data = map_data

            # Publish map
            self.map_pub.publish(map_msg)

        except Exception as e:
            self.get_logger().error(f'Error publishing map: {e}')

    def publish_trajectory(self):
        """Publish robot trajectory path"""
        try:
            path_msg = Path()
            path_msg.header = Header()
            path_msg.header.stamp = self.get_clock().now().to_msg()
            path_msg.header.frame_id = self.map_frame

            # Add poses to path (sample every 10th pose to reduce size)
            for i, pose_matrix in enumerate(self.trajectory_poses[::10]):
                pose_stamped = PoseStamped()
                pose_stamped.header = path_msg.header
                pose_stamped.pose.position.x = float(pose_matrix[0, 3])
                pose_stamped.pose.position.y = float(pose_matrix[1, 3])
                pose_stamped.pose.position.z = float(pose_matrix[2, 3])

                # Convert rotation matrix to quaternion
                rotation_matrix = pose_matrix[:3, :3]
                r = R.from_matrix(rotation_matrix)
                quat = r.as_quat()
                pose_stamped.pose.orientation.x = float(quat[0])
                pose_stamped.pose.orientation.y = float(quat[1])
                pose_stamped.pose.orientation.z = float(quat[2])
                pose_stamped.pose.orientation.w = float(quat[3])

                path_msg.poses.append(pose_stamped)

            # Publish trajectory
            self.trajectory_pub.publish(path_msg)

        except Exception as e:
            self.get_logger().error(f'Error publishing trajectory: {e}')


def main(args=None):
    rclpy.init(args=args)

    node = VSLAMProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()