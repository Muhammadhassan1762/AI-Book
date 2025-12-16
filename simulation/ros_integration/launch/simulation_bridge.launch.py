import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Package names
    pkg_simulation = FindPackageShare('simulation')
    pkg_ros_integration = FindPackageShare('ros_integration')

    # Unity bridge node
    unity_bridge_node = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        name='unity_bridge',
        parameters=[
            PathJoinSubstitution([pkg_ros_integration, 'config', 'unity_bridge.yaml']),
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    # Environment manager node
    env_manager_node = Node(
        package='gazebo_ros',
        executable='environment_manager',
        name='env_manager',
        parameters=[
            PathJoinSubstitution([pkg_ros_integration, 'config', 'environment_config.yaml']),
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    # Digital twin synchronizer node
    twin_sync_node = Node(
        package='digital_twin',
        executable='twin_synchronizer',
        name='twin_synchronizer',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'sync_frequency': 10.0},
            {'sync_tolerance': 0.1}
        ],
        output='screen'
    )

    # Sensor simulator node
    sensor_sim_node = Node(
        package='gazebo_ros',
        executable='sensor_simulator',
        name='sensor_simulator',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'publish_frequency': 30.0}
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        unity_bridge_node,
        env_manager_node,
        twin_sync_node,
        sensor_sim_node
    ])