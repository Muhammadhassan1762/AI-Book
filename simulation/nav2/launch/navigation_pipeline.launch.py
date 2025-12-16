import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, EmitEvent
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, LifecycleNode
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Package names
    pkg_nav2 = FindPackageShare('nav2')
    pkg_simulation = FindPackageShare('simulation')
    pkg_isaac_ros = FindPackageShare('isaac_ros')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    autostart = LaunchConfiguration('autostart', default='true')
    params_file = LaunchConfiguration('params_file', default='nav2_config.yaml')
    map_file = LaunchConfiguration('map', default='')
    use_composition = LaunchConfiguration('use_composition', default='False')
    use_respawn = LaunchConfiguration('use_respawn', default='False')
    log_level = LaunchConfiguration('log_level', default='info')

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Isaac Sim) clock if true'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value='nav2_config.yaml',
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )

    declare_map_file_cmd = DeclareLaunchArgument(
        'map',
        default_value='',
        description='Full path to map file to load'
    )

    declare_use_composition_cmd = DeclareLaunchArgument(
        'use_composition',
        default_value='False',
        description='Use composed bringup if True'
    )

    declare_use_respawn_cmd = DeclareLaunchArgument(
        'use_respawn',
        default_value='False',
        description='Whether to respawn if a node crashes'
    )

    declare_log_level_cmd = DeclareLaunchArgument(
        'log_level',
        default_value='info',
        description='log level'
    )

    # Lifecycle nodes
    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'recoveries_server',
        'bt_navigator',
        'waypoint_follower',
        'velocity_smoother'
    ]

    # Map server node
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'yaml_filename': map_file
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # Lifecycle manager for map server
    lifecycle_manager_map = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'autostart': autostart,
                'node_names': ['map_server']
            }
        ],
        output='screen'
    )

    # Lifecycle manager for navigation nodes
    lifecycle_manager_nav = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'autostart': autostart,
                'node_names': lifecycle_nodes
            }
        ],
        output='screen'
    )

    # AMCL node
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # Controller server node
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # Planner server node
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # BT Navigator
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # Velocity smoother
    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('cmd_vel', 'cmd_vel_smooth'),
            ('cmd_vel_smoothed', 'cmd_vel')
        ],
        output='screen'
    )

    # Recovery server
    recovery_server = Node(
        package='nav2_recoveries',
        executable='recoveries_server',
        name='recoveries_server',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # Waypoint follower
    waypoint_follower = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        output='screen'
    )

    # Nav2 interface node (custom)
    nav2_interface = Node(
        package='nav2',
        executable='nav2_interface',
        name='nav2_interface',
        parameters=[
            PathJoinSubstitution([pkg_simulation, 'nav2', 'config', params_file]),
            {
                'use_sim_time': use_sim_time,
                'robot_base_frame': 'base_link',
                'global_frame': 'map',
                'planner_frequency': 1.0,
                'controller_frequency': 20.0,
                'max_linear_speed': 0.5,
                'max_angular_speed': 1.0,
                'goal_tolerance': 0.25,
                'avoid_collision': True
            }
        ],
        remappings=[
            ('/vslam/map', '/vslam/map'),
            ('/vslam/pose', '/vslam/pose'),
            ('/initialpose', '/initialpose'),
            ('/clicked_goal', '/clicked_goal')
        ],
        output='screen'
    )

    # Add nodes to launch description
    ld = LaunchDescription()

    # Add launch arguments
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_map_file_cmd)
    ld.add_action(declare_use_composition_cmd)
    ld.add_action(declare_use_respawn_cmd)
    ld.add_action(declare_log_level_cmd)

    # Add nodes
    ld.add_action(lifecycle_manager_map)
    ld.add_action(lifecycle_manager_nav)
    ld.add_action(map_server)
    ld.add_action(amcl)
    ld.add_action(controller_server)
    ld.add_action(planner_server)
    ld.add_action(bt_navigator)
    ld.add_action(velocity_smoother)
    ld.add_action(recovery_server)
    ld.add_action(waypoint_follower)
    ld.add_action(nav2_interface)

    return ld