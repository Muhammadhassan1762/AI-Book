from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ros2_fundamentals_examples',
            executable='basic_publisher',
            name='basic_publisher',
            output='screen'
        ),
        Node(
            package='ros2_fundamentals_examples',
            executable='basic_subscriber',
            name='basic_subscriber',
            output='screen'
        )
    ])