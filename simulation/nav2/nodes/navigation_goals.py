#!/usr/bin/env python3
"""
Navigation Goals Handler Node

This ROS 2 node handles navigation goal requests and interfaces with the Nav2 system
for humanoid robot navigation.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid, Path
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import LoadMap, ClearEntireCostmap
from std_msgs.msg import String, Float32
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf_transformations
import math
from typing import Optional


class NavigationGoalsHandler(Node):
    def __init__(self):
        super().__init__('navigation_goals_handler')

        # Declare parameters
        self.declare_parameter('robot_base_frame', 'base_link')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('goal_frame', 'map')
        self.declare_parameter('planner_frequency', 1.0)
        self.declare_parameter('controller_frequency', 20.0)
        self.declare_parameter('max_linear_speed', 0.3)  # Reduced for humanoid stability
        self.declare_parameter('max_angular_speed', 0.6)  # Reduced for humanoid stability
        self.declare_parameter('goal_tolerance', 0.25)
        self.declare_parameter('yaw_goal_tolerance', 0.25)
        self.declare_parameter('avoid_collision', True)
        self.declare_parameter('use_sim_time', True)

        # Get parameters
        self.robot_base_frame = self.get_parameter('robot_base_frame').value
        self.map_frame = self.get_parameter('map_frame').value
        self.goal_frame = self.get_parameter('goal_frame').value
        self.planner_frequency = self.get_parameter('planner_frequency').value
        self.controller_frequency = self.get_parameter('controller_frequency').value
        self.max_linear_speed = self.get_parameter('max_linear_speed').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.goal_tolerance = self.get_parameter('goal_tolerance').value
        self.yaw_goal_tolerance = self.get_parameter('yaw_goal_tolerance').value
        self.avoid_collision = self.get_parameter('avoid_collision').value
        self.use_sim_time = self.get_parameter('use_sim_time').value

        # Initialize TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # QoS profiles
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Create action clients
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

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
        self.nav_status_pub = self.create_publisher(String, '/nav2/status', qos_profile)
        self.nav_progress_pub = self.create_publisher(Float32, '/nav2/progress', qos_profile)

        # Create services
        self.clear_costmap_srv = self.create_service(
            ClearEntireCostmap,
            'clear_costmap',
            self.clear_costmap_callback
        )

        # Initialize state variables
        self.current_map = None
        self.current_pose = None
        self.navigation_active = False
        self.navigation_goal = None
        self.navigation_progress = 0.0
        self.navigation_result = None

        # Create timers
        self.status_timer = self.create_timer(1.0, self.publish_status)
        self.navigation_timer = self.create_timer(1.0/self.planner_frequency, self.navigation_tick)

        self.get_logger().info('Navigation Goals Handler node initialized')

    def vslam_map_callback(self, msg):
        """Receive map from VSLAM system"""
        self.current_map = msg
        self.get_logger().debug(f'Received map from VSLAM with resolution {msg.info.resolution}')

    def vslam_pose_callback(self, msg):
        """Receive pose estimate from VSLAM system"""
        self.current_pose = msg
        self.get_logger().debug(f'Received pose from VSLAM: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})')

    def initial_pose_callback(self, msg):
        """Receive initial pose for the robot"""
        self.get_logger().info('Setting initial pose for localization')
        # In a real implementation, this would set the initial pose for AMCL

    def clicked_goal_callback(self, msg):
        """Receive navigation goal from user interface"""
        self.get_logger().info(f'Received navigation goal: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})')

        # Validate goal
        if self.validate_goal(msg):
            # Send the goal to Nav2
            self.send_navigation_goal(msg)
        else:
            self.get_logger().warn('Received goal is invalid, ignoring')

    def validate_goal(self, goal_pose_stamped):
        """Validate that the goal is reachable and safe"""
        if self.current_map is None:
            self.get_logger().warn('No map available for goal validation')
            return False

        # Convert goal position to map coordinates
        try:
            map_x = int((goal_pose_stamped.pose.position.x - self.current_map.info.origin.position.x) / self.current_map.info.resolution)
            map_y = int((goal_pose_stamped.pose.position.y - self.current_map.info.origin.position.y) / self.current_map.info.resolution)

            # Check bounds
            if (map_x < 0 or map_x >= self.current_map.info.width or
                map_y < 0 or map_y >= self.current_map.info.height):
                self.get_logger().warn('Goal is outside map bounds')
                return False

            # Check if goal is in free space (cell value < 50 means mostly free)
            map_index = map_y * self.current_map.info.width + map_x
            if map_index < len(self.current_map.data):
                cell_value = self.current_map.data[map_index]
                if cell_value > 50:  # Occupied or highly costly
                    self.get_logger().warn('Goal is in occupied space')
                    return False
            else:
                self.get_logger().warn('Map index out of bounds')
                return False

            return True

        except Exception as e:
            self.get_logger().error(f'Error validating goal: {e}')
            return False

    def send_navigation_goal(self, goal_pose_stamped):
        """Send navigation goal to Nav2 system"""
        if not self.nav_to_pose_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Navigation action server not available')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose_stamped

        self.get_logger().info(f'Sending navigation goal to Nav2: ({goal_msg.pose.pose.position.x:.2f}, {goal_msg.pose.pose.position.y:.2f})')

        self.navigation_active = True
        self.navigation_goal = goal_pose_stamped

        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.navigation_feedback_callback
        )

        send_goal_future.add_done_callback(self.navigation_response_callback)

    def navigation_response_callback(self, future):
        """Handle navigation goal response"""
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().info('Navigation goal rejected')
                self.navigation_active = False
                return

            self.get_logger().info('Navigation goal accepted')
            self.navigation_active = True

            get_result_future = goal_handle.get_result_async()
            get_result_future.add_done_callback(self.navigation_result_callback)

        except Exception as e:
            self.get_logger().error(f'Error in navigation response: {e}')
            self.navigation_active = False

    def navigation_feedback_callback(self, feedback_msg):
        """Handle navigation feedback"""
        try:
            feedback = feedback_msg.feedback

            # Update progress based on feedback
            # The feedback typically contains information about progress
            # In a real implementation, we would use actual progress data
            self.navigation_progress = getattr(feedback, 'distance_remaining', 0.0)

            self.get_logger().debug(f'Navigation feedback: {self.navigation_progress:.2f}m remaining')

        except Exception as e:
            self.get_logger().error(f'Error in navigation feedback: {e}')

    def navigation_result_callback(self, future):
        """Handle navigation result"""
        try:
            result = future.result().result
            self.navigation_result = result
            self.get_logger().info(f'Navigation result: {result}')
            self.navigation_active = False
            self.navigation_progress = 0.0

        except Exception as e:
            self.get_logger().error(f'Error in navigation result: {e}')
            self.navigation_active = False

    def publish_status(self):
        """Publish navigation status updates"""
        status_msg = String()

        if self.navigation_active:
            status_msg.data = f"Navigation active - Goal: ({self.navigation_goal.pose.position.x:.2f}, {self.navigation_goal.pose.position.y:.2f})"
        else:
            if self.navigation_result:
                status_msg.data = f"Navigation completed with result: {self.navigation_result}"
            else:
                status_msg.data = "Navigation idle - Ready for goals"

        self.nav_status_pub.publish(status_msg)

        # Publish progress
        progress_msg = Float32()
        progress_msg.data = float(self.navigation_progress)
        self.nav_progress_pub.publish(progress_msg)

    def navigation_tick(self):
        """Periodic navigation processing"""
        # This method is called periodically to handle navigation logic
        # In a real implementation, this would handle path re-planning, obstacle avoidance, etc.
        pass

    def clear_costmap_callback(self, request, response):
        """Service callback to clear costmaps"""
        self.get_logger().info('Clearing costmaps')
        # In a real implementation, this would call the clear_costmap service

        response.result = True
        return response

    def get_robot_position(self):
        """Get the current robot position from TF or VSLAM"""
        if self.current_pose:
            return self.current_pose.pose.position
        else:
            try:
                # Try to get robot position from TF
                transform = self.tf_buffer.lookup_transform(
                    self.map_frame,
                    self.robot_base_frame,
                    rclpy.time.Time(),
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )

                pos = transform.transform.translation
                return pos
            except TransformException as ex:
                self.get_logger().warn(f'Could not lookup transform: {ex}')
                return None

    def cancel_current_goal(self):
        """Cancel the currently active navigation goal"""
        self.get_logger().info('Canceling current navigation goal')
        # In a real implementation, this would cancel the current goal
        self.navigation_active = False
        self.navigation_goal = None
        self.navigation_progress = 0.0


def main(args=None):
    rclpy.init(args=args)

    node = NavigationGoalsHandler()

    # Use multi-threaded executor to handle callbacks
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()