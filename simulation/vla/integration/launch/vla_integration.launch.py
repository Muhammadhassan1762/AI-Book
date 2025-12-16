from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launch file for complete VLA integration pipeline.

    This launch file starts the complete Vision-Language-Action pipeline
    that integrates Whisper, LLM planner, and execution components.
    """
    # Get package share directory
    package_dir = get_package_share_directory('vla_integration')

    # Load configuration file
    config_file = os.path.join(
        package_dir,
        'config',
        'vla_config.yaml'
    )

    return LaunchDescription([
        # VLA integration pipeline node
        Node(
            package='vla_integration',
            executable='vla_pipeline',
            name='vla_pipeline_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        ),

        # Safety validator node
        Node(
            package='vla_integration',
            executable='safety_validator',
            name='safety_validator_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        ),

        # VLA context manager node
        Node(
            package='vla_integration',
            executable='vla_context_manager',
            name='vla_context_manager_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        )
    ])