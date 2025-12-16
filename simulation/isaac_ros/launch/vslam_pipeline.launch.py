import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Package names
    pkg_isaac_ros = FindPackageShare('isaac_ros')
    pkg_simulation = FindPackageShare('simulation')

    # Launch configuration variables
    rgb_topic = LaunchConfiguration('rgb_topic', default='/camera/rgb/image_rect_color')
    depth_topic = LaunchConfiguration('depth_topic', default='/camera/depth/image_rect_raw')
    config_file = LaunchConfiguration('config_file', default='vslam_config.yaml')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Declare launch arguments
    declare_rgb_topic_cmd = DeclareLaunchArgument(
        'rgb_topic',
        default_value='/camera/rgb/image_rect_color',
        description='Topic name for RGB camera input'
    )

    declare_depth_topic_cmd = DeclareLaunchArgument(
        'depth_topic',
        default_value='/camera/depth/image_rect_raw',
        description='Topic name for depth camera input'
    )

    declare_config_file_cmd = DeclareLaunchArgument(
        'config_file',
        default_value='vslam_config.yaml',
        description='Name of the VSLAM configuration file'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Isaac Sim) clock if true'
    )

    # VSLAM processor node
    vslam_processor = Node(
        package='isaac_ros',
        executable='vslam_processor',
        name='vslam_processor',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'isaac_ros', 'config', config_file]),
            {
                'rgb_topic': rgb_topic,
                'depth_topic': depth_topic,
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            (rgb_topic, rgb_topic),
            (depth_topic, depth_topic)
        ],
        output='screen'
    )

    # Optional: Pose estimation node
    pose_estimator = Node(
        package='isaac_ros',
        executable='pose_estimator',
        name='pose_estimator',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'base_frame': 'base_link',
                'camera_frame': 'camera_link',
                'map_frame': 'map'
            }
        ],
        output='screen'
    )

    # Optional: Map generation node
    map_generator = Node(
        package='isaac_ros',
        executable='map_generator',
        name='map_generator',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'map_frame': 'map',
                'resolution': 0.05,
                'publish_rate': 1.0
            }
        ],
        output='screen'
    )

    ld = LaunchDescription()

    # Add launch arguments
    ld.add_action(declare_rgb_topic_cmd)
    ld.add_action(declare_depth_topic_cmd)
    ld.add_action(declare_config_file_cmd)
    ld.add_action(declare_use_sim_time_cmd)

    # Add nodes
    ld.add_action(vslam_processor)
    ld.add_action(pose_estimator)
    ld.add_action(map_generator)

    return ld