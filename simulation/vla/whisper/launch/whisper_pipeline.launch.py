from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launch file for Whisper speech-to-text pipeline in VLA system.

    This launch file starts the Whisper speech recognition node that converts
    audio input to text commands for the VLA system.
    """
    # Get package share directory
    package_dir = get_package_share_directory('vla_whisper')

    # Load configuration file
    config_file = os.path.join(
        package_dir,
        'config',
        'whisper_config.yaml'
    )

    return LaunchDescription([
        # Whisper speech-to-text node
        Node(
            package='vla_whisper',
            executable='speech_to_text',
            name='whisper_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        ),

        # Audio input processing node
        Node(
            package='vla_whisper',
            executable='audio_processor',
            name='audio_processor_node',
            parameters=[config_file],
            output='screen',
            emulate_tty=True
        )
    ])