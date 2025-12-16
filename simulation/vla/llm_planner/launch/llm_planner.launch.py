from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launch file for LLM-based cognitive planning in VLA system.

    This launch file starts the LLM planner node that converts natural language
    commands to ROS action sequences for the VLA system.
    """
    # Get package share directory
    package_dir = get_package_share_directory('vla_llm_planner')

    # Load configuration file
    config_file = os.path.join(
        package_dir,
        'config',
        'llm_config.yaml'
    )

    return LaunchDescription([
        # LLM cognitive planner node
        Node(
            package='vla_llm_planner',
            executable='cognitive_planner',
            name='llm_planner_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        ),

        # Action generator node
        Node(
            package='vla_llm_planner',
            executable='action_generator',
            name='action_generator_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        ),

        # Command mapper node
        Node(
            package='vla_llm_planner',
            executable='command_mapper',
            name='command_mapper_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        )
    ])