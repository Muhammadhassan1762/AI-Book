from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    urdf_model_path = LaunchConfiguration('model')

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value='simulation/models/simple_humanoid/model.urdf',
            description='URDF path to the model file'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_model_path).read()}]
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', 'config/urdf.rviz']
        )
    ])