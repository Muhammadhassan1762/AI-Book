#!/usr/bin/env python3
"""
Pose Estimator Node

This ROS 2 node estimates the 6D pose of the camera/robot from visual input
using feature matching and geometric algorithms.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped, TransformStamped
from std_msgs.msg import Header
from cv_bridge import CvBridge
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R
import tf2_ros
from geometry_msgs.msg import Point, Quaternion


class PoseEstimator(Node):
    def __init__(self):
        super().__init__('pose_estimator')

        # Declare parameters
        self.declare_parameter('camera_topic', '/camera/rgb/image_rect_color')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('camera_frame', 'camera_link')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('max_features', 1000)
        self.declare_parameter('min_features', 50)
        self.declare_parameter('reproj_threshold', 2.0)
        self.declare_parameter('min_inliers', 10)
        self.declare_parameter('publish_rate', 30.0)

        # Get parameters
        self.camera_topic = self.get_parameter('camera_topic').value
        self.base_frame = self.get_parameter('base_frame').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.map_frame = self.get_parameter('map_frame').value
        self.max_features = self.get_parameter('max_features').value
        self.min_features = self.get_parameter('min_features').value
        self.reproj_threshold = self.get_parameter('reproj_threshold').value
        self.min_inliers = self.get_parameter('min_inliers').value
        self.publish_rate = self.get_parameter('publish_rate').value

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Initialize feature detector and matcher
        self.detector = cv2.ORB_create(nfeatures=self.max_features)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

        # Camera intrinsic parameters (should be loaded from calibration)
        self.camera_matrix = np.array([
            [384.0, 0.0, 320.0],
            [0.0, 384.0, 240.0],
            [0.0, 0.0, 1.0]
        ])

        # Initialize pose tracking
        self.current_pose = np.eye(4)  # 4x4 transformation matrix
        self.previous_keypoints = None
        self.previous_descriptors = None
        self.reference_points_3d = []  # 3D points in reference frame
        self.reference_points_2d = []  # 2D points in reference image

        # QoS profile for sensor data
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            sensor_qos
        )

        # Create publishers
        self.pose_pub = self.create_publisher(PoseStamped, '/vslam/pose', 10)

        # Create TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Initialize reference pose
        self.initial_pose_set = False

        self.get_logger().info('Pose Estimator node initialized')

    def image_callback(self, msg):
        """Process incoming image for pose estimation"""
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Detect features in current image
            current_keypoints, current_descriptors = self.detector.detectAndCompute(cv_image, None)

            if current_descriptors is not None and len(current_keypoints) >= self.min_features:
                if self.previous_descriptors is not None:
                    # Match features between previous and current frame
                    matches = self.matcher.knnMatch(
                        self.previous_descriptors, current_descriptors, k=2
                    )

                    # Apply Lowe's ratio test for good matches
                    good_matches = []
                    for match_pair in matches:
                        if len(match_pair) == 2:
                            m, n = match_pair
                            if m.distance < 0.75 * n.distance:
                                good_matches.append(m)

                    if len(good_matches) >= self.min_inliers:
                        # Extract matched points
                        prev_pts = np.float32([self.previous_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                        curr_pts = np.float32([current_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                        # Estimate motion using essential matrix
                        E, mask = cv2.findEssentialMat(
                            curr_pts, prev_pts, self.camera_matrix,
                            method=cv2.RANSAC, prob=0.999, threshold=self.reproj_threshold
                        )

                        if E is not None:
                            # Recover pose from essential matrix
                            _, R, t, _ = cv2.recoverPose(E, curr_pts, prev_pts, self.camera_matrix)

                            # Create transformation matrix
                            T_delta = np.eye(4)
                            T_delta[:3, :3] = R
                            T_delta[:3, 3] = t.flatten()

                            # Update current pose
                            self.current_pose = self.current_pose @ T_delta

                            # Publish pose
                            self.publish_pose(msg.header.stamp)

                # Update previous frame data
                self.previous_keypoints = current_keypoints
                self.previous_descriptors = current_descriptors

        except Exception as e:
            self.get_logger().error(f'Error processing image for pose estimation: {e}')

    def publish_pose(self, stamp):
        """Publish the estimated pose"""
        try:
            # Create PoseStamped message
            pose_msg = PoseStamped()
            pose_msg.header = Header()
            pose_msg.header.stamp = stamp
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
            t.header.stamp = stamp
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

    def reset_pose(self):
        """Reset the estimated pose to identity"""
        self.current_pose = np.eye(4)
        self.previous_keypoints = None
        self.previous_descriptors = None
        self.initial_pose_set = False
        self.get_logger().info('Pose estimator reset')


def main(args=None):
    rclpy.init(args=args)

    node = PoseEstimator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()