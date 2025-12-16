---
sidebar_position: 1
---

# Chapter 3: Advanced Navigation with Nav2

## Cognitive Navigation for Humanoid Robots

Navigation is a fundamental capability for humanoid robots, enabling them to move autonomously in complex environments. This chapter covers advanced navigation techniques using the Navigation2 (Nav2) framework, specifically tailored for humanoid robots with vision-language-action capabilities.

## Learning Objectives

By the end of this chapter, you will:
- Understand the Nav2 architecture and its components
- Configure navigation for humanoid robot kinematics
- Implement cognitive navigation with semantic understanding
- Integrate vision-language systems with navigation
- Handle dynamic environments and human-aware navigation
- Optimize navigation for real-time performance
- Validate navigation systems for safety and reliability

## Introduction to Navigation2

### Nav2 Architecture Overview

Navigation2 (Nav2) is the next-generation navigation framework for ROS 2, designed to be more flexible, robust, and capable than its predecessor. The architecture is built around behavior trees, allowing for complex decision-making and recovery behaviors.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Perception    │───▶│   Planning      │───▶│   Execution     │
│   (SLAM/Maps)   │    │   (Path/Action) │    │   (Controllers) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Costmap         │    │ Global Planner  │    │ Local Planner   │
│ Management      │    │ (A*, Dijkstra)  │    │ (DWA, MPC)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Obstacle        │    │ Path            │    │ Velocity        │
│ Avoidance       │    │ Optimization    │    │ Commands        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

1. **Global Planner**: Creates optimal path from start to goal
2. **Local Planner**: Generates velocity commands to follow path
3. **Controller**: Executes low-level motor commands
4. **Recovery Behaviors**: Handles navigation failures
5. **Sensors**: Provides perception data
6. **Transforms**: Manages coordinate frames

## Nav2 Configuration for Humanoid Robots

### Humanoid-Specific Navigation Parameters

```yaml
# nav2_params_humanoid.yaml
amcl:
  ros__parameters:
    use_sim_time: true
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_link"
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beamskip: false
    global_frame_id: "map"
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 100.0
    laser_min_range: -1.0
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    odom_frame_id: "odom"
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_thresh: 0.5
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    save_pose_rate: 0.5
    sigma_hit: 0.2
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.2
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05
    scan_topic: scan

amcl_map_client:
  ros__parameters:
    use_sim_time: true

amcl_rclcpp_node:
  ros__parameters:
    use_sim_time: true

bt_navigator:
  ros__parameters:
    use_sim_time: true
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    # Enables dynamic replanning when new path is computed
    enable_loopback: true
    # Frequencies to run BT at
    # 0.0 will use the rate of the main nav loop (10Hz default)
    action_server_rate: 0.0
    # Plugins for BT Navigator
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_back_up_action_bt_node
    - nav2_spin_action_bt_node
    - nav2_wait_action_bt_node
    - nav2_clear_costmap_service_bt_node
    - nav2_is_stuck_condition_bt_node
    - nav2_goal_reached_condition_bt_node
    - nav2_goal_updated_condition_bt_node
    - nav2_initial_pose_received_condition_bt_node
    - nav2_reinitialize_global_localization_service_bt_node
    - nav2_rate_controller_bt_node
    - nav2_distance_controller_bt_node
    - nav2_speed_controller_bt_node
    - nav2_truncate_path_action_bt_node
    - nav2_goal_updater_node_bt_node
    - nav2_recovery_node_bt_node
    - nav2_pipeline_sequence_bt_node
    - nav2_round_robin_node_bt_node
    - nav2_transform_available_condition_bt_node
    - nav2_time_expired_condition_bt_node
    - nav2_path_expiring_timer_condition
    - nav2_distance_traveled_condition_bt_node
    - nav2_single_trigger_bt_node
    - nav2_is_path_valid_condition_bt_node
    - nav2_globally_consistent_localizer_bt_node
    - nav2_is_battery_low_condition_bt_node
    - nav2_navigate_through_poses_action_bt_node
    - nav2_navigate_to_pose_action_bt_node

bt_navigator_rclcpp_node:
  ros__parameters:
    use_sim_time: true

controller_server:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # DWB parameters
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: True
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.5  # Reduced for humanoid stability
      max_vel_y: 0.5
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 5
      vtheta_samples: 20
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25  # Increased for humanoid feet placement
      yaw_goal_tolerance: 0.25
      stateful: True
      global_plan_overwrite_orientation: True
      prune_plan: True
      prune_distance: 1.0
      oscillation_reset_dist: 0.05
      deviate_angle: 1.571
      latch_xy_goal_tolerance: False
      # Humanoid-specific parameters
      step_size: 0.05  # Smaller steps for careful foot placement
      max_approach_velocity: 0.3  # Conservative approach speed for stability

    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.3  # Larger tolerance for humanoid feet placement
      yaw_goal_tolerance: 0.3
      stateful: True

controller_server_rclcpp_node:
  ros__parameters:
    use_sim_time: true

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: true
      rolling_window: true
      width: 6  # Smaller window for humanoid agility
      height: 6
      resolution: 0.05  # Higher resolution for detailed obstacle detection
      robot_radius: 0.4  # Larger radius for humanoid safety
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0  # Higher cost scaling for safety
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: False
        origin_z: 0.0
        z_resolution: 0.2
        z_voxels: 10
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
  local_costmap_client:
    ros__parameters:
      use_sim_time: true
  local_costmap_rclcpp_node:
    ros__parameters:
      use_sim_time: true

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: true
      robot_radius: 0.4
      resolution: 0.05  # Higher resolution for detailed planning
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
  global_costmap_client:
    ros__parameters:
      use_sim_time: true
  global_costmap_rclcpp_node:
    ros__parameters:
      use_sim_time: true

planner_server:
  ros__parameters:
    expected_planner_frequency: 2.0
    use_sim_time: true
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5  # Increased tolerance for humanoid path feasibility
      use_astar: false
      allow_unknown: true
      # Humanoid-specific parameters
      step_size: 0.05  # Finer resolution for detailed path planning
      min_distance_to_obstacle: 0.45  # Maintain safety distance

planner_server_rclcpp_node:
  ros__parameters:
    use_sim_time: true

recoveries_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    recovery_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_recoveries/Spin"
      sim_frequency: 25.0
      angle_target: 1.57
      angle_tolerance: 0.1
      # Humanoid-specific: slower, more controlled spinning
      max_angular_velocity: 0.5
      min_angular_velocity: 0.1
    backup:
      plugin: "nav2_recoveries/BackUp"
      sim_frequency: 50.0
      # Humanoid-specific: careful backward movement
      distance: 0.3
      backup_speed: 0.05
    wait:
      plugin: "nav2_recoveries/Wait"
      sim_frequency: 10.0
      # Humanoid-specific: longer wait times for dynamic obstacles
      wait_duration: 5.0

robot_state_publisher:
  ros__parameters:
    use_sim_time: true

waypoint_follower:
  ros__parameters:
    loop_rate: 20
    stop_on_failure: false
    goal_check_tolerance: 0.25  # Humanoid-appropriate tolerance
    # Humanoid-specific waypoint following
    max_linear_velocity: 0.4
    min_linear_velocity: 0.1
    max_angular_velocity: 0.6