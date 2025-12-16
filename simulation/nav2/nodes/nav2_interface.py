#!/usr/bin/env python3
"""
Nav2 Interface Node

This ROS 2 node provides an interface to the Nav2 navigation system,
allowing for path planning and navigation execution based on VSLAM maps.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid, Path
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String, Float32
from geometry_msgs.msg import Pose, Point, Quaternion
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf_transformations
import math


class Nav2Interface(Node):
    def __init__(self):
        super().__init__('nav2_interface')

        # Declare parameters
        self.declare_parameter('robot_base_frame', 'base_link')
        self.declare_parameter('global_frame', 'map')
        self.declare_parameter('planner_frequency', 1.0)
        self.declare_parameter('controller_frequency', 20.0)
        self.declare_parameter('max_linear_speed', 0.5)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('goal_tolerance', 0.25)
        self.declare_parameter('avoid_collision', True)

        # Get parameters
        self.robot_base_frame = self.get_parameter('robot_base_frame').value
        self.global_frame = self.get_parameter('global_frame').value
        self.planner_frequency = self.get_parameter('planner_frequency').value
        self.controller_frequency = self.get_parameter('controller_frequency').value
        self.max_linear_speed = self.get_parameter('max_linear_speed').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.goal_tolerance = self.get_parameter('goal_tolerance').value
        self.avoid_collision = self.get_parameter('avoid_collision').value

        # Initialize TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # QoS profiles
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Create subscribers
        self.vslam_map_sub = self.create_subscription(
            OccupancyGrid,
            '/vslam/map',
            self.vslam_map_callback,
            qos_profile
        )

        self.vslam_pose_sub = self.create_subscription(
            PoseStamped,
            '/vslam/pose',
            self.vslam_pose_callback,
            qos_profile
        )

        self.initial_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/initialpose',
            self.initial_pose_callback,
            qos_profile
        )

        self.clicked_goal_sub = self.create_subscription(
            PoseStamped,
            '/clicked_goal',
            self.clicked_goal_callback,
            qos_profile
        )

        # Create publishers
        self.nav_plan_pub = self.create_publisher(Path, '/nav2/plan', qos_profile)
        self.nav_cmd_vel_pub = self.create_publisher(Float32, '/nav2/cmd_vel', qos_profile)
        self.nav_progress_pub = self.create_publisher(Float32, '/nav2/progress', qos_profile)
        self.nav_status_pub = self.create_publisher(String, '/nav2/status', qos_profile)

        # Create action client for navigation
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Initialize state variables
        self.current_map = None
        self.current_pose = None
        self.navigation_active = False
        self.navigation_goal = None
        self.navigation_progress = 0.0

        # Create timer for status updates
        self.status_timer = self.create_timer(1.0, self.publish_status)

        self.get_logger().info('Nav2 Interface node initialized')

    def vslam_map_callback(self, msg):
        """Receive map from VSLAM system"""
        self.current_map = msg
        self.get_logger().debug('Received map from VSLAM')

    def vslam_pose_callback(self, msg):
        """Receive pose estimate from VSLAM system"""
        self.current_pose = msg
        self.get_logger().debug(f'Received pose from VSLAM: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})')

    def initial_pose_callback(self, msg):
        """Receive initial pose for the robot"""
        self.get_logger().info('Setting initial pose for localization')

    def clicked_goal_callback(self, msg):
        """Receive navigation goal from user interface"""
        self.get_logger().info(f'Received navigation goal: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})')

        # Send the goal to Nav2
        self.send_navigation_goal(msg)

    def send_navigation_goal(self, goal_pose_stamped):
        """Send navigation goal to Nav2 system"""
        if not self.nav_to_pose_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Navigation action server not available')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose_stamped

        self.get_logger().info(f'Sending navigation goal to Nav2: ({goal_msg.pose.pose.position.x:.2f}, {goal_msg.pose.pose.position.y:.2f})')

        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.navigation_feedback_callback
        )

        send_goal_future.add_done_callback(self.navigation_response_callback)

    def navigation_response_callback(self, future):
        """Handle navigation goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Navigation goal rejected')
            return

        self.get_logger().info('Navigation goal accepted')
        self.navigation_active = True

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.navigation_result_callback)

    def navigation_feedback_callback(self, feedback_msg):
        """Handle navigation feedback"""
        feedback = feedback_msg.feedback
        # Update progress based on feedback
        self.navigation_progress = getattr(feedback, 'distance_remaining', 0.0)

    def navigation_result_callback(self, future):
        """Handle navigation result"""
        result = future.result().result
        self.get_logger().info(f'Navigation result: {result}')
        self.navigation_active = False
        self.navigation_progress = 0.0

    def publish_status(self):
        """Publish navigation status updates"""
        if self.navigation_active:
            status_msg = String()
            status_msg.data = f"Navigation in progress - Progress: {self.navigation_progress:.2f}"
            self.nav_status_pub.publish(status_msg)
        else:
            status_msg = String()
            status_msg.data = "Navigation idle"
            self.nav_status_pub.publish(status_msg)

        # Publish progress
        progress_msg = Float32()
        progress_msg.data = float(self.navigation_progress)
        self.nav_progress_pub.publish(progress_msg)

    def compute_path_to_pose(self, start_pose, goal_pose):
        """Compute path to a specific pose without executing"""
        # This would interface with the Nav2 path planner
        # For now, return a simple path
        path_msg = Path()
        path_msg.header.frame_id = self.global_frame

        # Create a straight line path (for demonstration)
        steps = 10
        dx = (goal_pose.pose.position.x - start_pose.pose.position.x) / steps
        dy = (goal_pose.pose.position.y - start_pose.pose.position.y) / steps

        for i in range(steps + 1):
            pose_stamped = PoseStamped()
            pose_stamped.header.frame_id = self.global_frame
            pose_stamped.pose.position.x = start_pose.pose.position.x + dx * i
            pose_stamped.pose.position.y = start_pose.pose.position.y + dy * i
            pose_stamped.pose.position.z = start_pose.pose.position.z

            # Keep the same orientation as start pose
            pose_stamped.pose.orientation = start_pose.pose.orientation

            path_msg.poses.append(pose_stamped)

        return path_msg

    def clear_costmaps(self):
        """Clear the navigation costmaps"""
        self.get_logger().info('Clearing costmaps')
        # In a real implementation, this would call the clear_costmaps service

    def get_robot_position(self):
        """Get the current robot position from TF or VSLAM"""
        if self.current_pose:
            return self.current_pose.pose.position
        else:
            try:
                # Try to get robot position from TF
                transform = self.tf_buffer.lookup_transform(
                    self.global_frame,
                    self.robot_base_frame,
                    rclpy.time.Time(),
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )

                pos = transform.transform.translation
                return Point(x=pos.x, y=pos.y, z=pos.z)
            except TransformException as ex:
                self.get_logger().warn(f'Could not lookup transform: {ex}')
                return None


def main(args=None):
    rclpy.init(args=args)

    node = Nav2Interface()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()