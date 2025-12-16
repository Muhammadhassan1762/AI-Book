from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ros2_fundamentals_examples',
            executable='ai_decision_node',
            name='ai_decision_node',
            output='screen'
        ),
        Node(
            package='ros2_fundamentals_examples',
            executable='robot_controller',
            name='robot_controller',
            output='screen'
        )
    ])