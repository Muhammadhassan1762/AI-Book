---
title: Nav2 Path Planning Concepts
sidebar_position: 2
---

# Nav2 Path Planning Concepts

This section covers the fundamental concepts and theoretical background of Navigation2 path planning, including algorithms, architectures, and practical implementation considerations for humanoid robots.

## Navigation2 Architecture

Navigation2 (Nav2) is the standard navigation framework for ROS 2, designed to plan and execute paths for mobile robots. It provides a flexible, plugin-based architecture that allows for custom navigation components.

### Core Components

The Nav2 system consists of several key components:

1. **Global Planner**: Plans long-term path from start to goal
2. **Local Planner**: Generates short-term trajectories considering obstacles
3. **Controller**: Executes velocity commands to follow planned path
4. **Costmap**: Represents environment with obstacles and free space
5. **Behavior Tree**: Coordinates navigation tasks and recovery behaviors

### System Architecture

```
[Map] → [Global Planner] → [Local Planner] → [Controller] → [Robot]
   ↑           ↓                ↓               ↓           ↓
[Localization] [Path]       [Trajectory]   [Commands]  [Feedback]
```

## Path Planning Algorithms

### Global Path Planning

Global planners create a path from the robot's current position to the goal position across the entire map.

#### A* Algorithm
A* is a popular pathfinding algorithm that uses heuristics to find the shortest path:
- **Advantages**: Optimal path, guaranteed to find solution if one exists
- **Disadvantages**: Can be computationally expensive
- **Use Case**: Static environments with known maps

#### Dijkstra's Algorithm
Dijkstra's algorithm finds the shortest path from a single source to all other nodes:
- **Advantages**: Guaranteed to find shortest path
- **Disadvantages**: Explores all directions equally, slower than A*
- **Use Case**: When heuristic function is difficult to define

#### NavFn Planner
NavFn is the default planner in Nav2, based on the Fast Marching Method:
- **Advantages**: Fast, reliable, works well with costmaps
- **Disadvantages**: Creates grid-aligned paths
- **Use Case**: General-purpose navigation with costmap integration

### Local Path Planning

Local planners generate short-term trajectories considering dynamic obstacles and robot kinematics.

#### Dynamic Window Approach (DWA)
DWA considers robot dynamics when generating trajectories:
- **Advantages**: Considers robot constraints, good for dynamic environments
- **Disadvantages**: Computationally intensive
- **Use Case**: Robots with significant dynamics constraints

#### Trajectory Rollout
Generates multiple potential trajectories and selects the best:
- **Advantages**: Flexible, can consider multiple objectives
- **Disadvantages**: Computationally expensive
- **Use Case**: Complex navigation scenarios with multiple objectives

## Costmap Representation

Costmaps represent the environment as a grid of values indicating traversability.

### Cell Values
- **0**: Free space
- **1-99**: Increasing cost (obstacle proximity)
- **100**: Occupied space
- **-1**: Unknown space

### Layers
Costmaps are built from multiple layers:
1. **Static Layer**: Predefined map
2. **Obstacle Layer**: Detected obstacles
3. **Inflation Layer**: Safety margins around obstacles

## Behavior Trees in Navigation

Nav2 uses behavior trees to coordinate navigation tasks and recovery behaviors.

### Tree Structure
```
NavigateToPose
├── ComputePathToPose
├── FollowPath
│   ├── IsStuck?
│   ├── SmoothPath?
│   ├── FollowWaypoints
│   └── IsGoalReached?
└── Recovery
    ├── Spin
    ├── BackUp
    └── Wait
```

### Advantages
- **Modularity**: Easy to modify individual behaviors
- **Flexibility**: Complex decision-making logic
- **Recovery**: Built-in failure handling
- **Monitoring**: Detailed execution tracking

## Humanoid-Specific Navigation

Humanoid robots have unique navigation requirements that differ from wheeled platforms.

### Stability Considerations
- **Balance**: Maintain center of mass within support polygon
- **Foot placement**: Plan steps that maintain balance
- **Transition time**: Allow time for balance recovery
- **Base of support**: Consider stance width and step length

### Movement Constraints
- **Limited turning**: Cannot turn in place like differential drive
- **Step size**: Limited by leg length and joint ranges
- **Walking speed**: Slower than wheeled robots
- **Terrain**: Limited to relatively flat surfaces

### Safety Requirements
- **Fall prevention**: Avoid obstacles that could cause falls
- **Recovery space**: Plan paths with room for recovery
- **Stability margins**: Larger safety buffers than wheeled robots
- **Emergency stops**: Quick stopping capabilities

## Navigation Parameters

### Critical Parameters

#### Global Planner
- **Tolerance**: Distance to goal for success (default: 0.5m)
- **Allow unknown**: Whether to plan through unknown space
- **Use A* vs Dijkstra**: Algorithm selection

#### Local Planner
- **XY tolerance**: Distance to goal position (default: 0.25m)
- **Yaw tolerance**: Angular tolerance at goal (default: 0.25 rad)
- **Controller frequency**: How often to update commands (default: 20Hz)
- **Velocity limits**: Max linear/angular velocities

#### Costmap Parameters
- **Resolution**: Cell size in meters (e.g., 0.05m)
- **Robot radius**: Radius for collision checking
- **Inflation radius**: Safety margin around obstacles
- **Update frequency**: How often to update costmap

## Implementation Patterns

### Configuration Structure

Nav2 uses YAML configuration files to define all parameters:

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBasedPlanner"]
    GridBasedPlanner:
      plugin: "nav2_navfn_planner::NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```

### Launch File Structure

Launch files define which nodes to run and their configurations:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server'
        )
    ])
```

## Performance Considerations

### Real-Time Requirements

Nav2 systems typically target:
- **Global planning**: 1-5 Hz (path updates)
- **Local planning**: 10-20 Hz (trajectory updates)
- **Control**: 20-50 Hz (velocity commands)

### Computational Complexity

Key bottlenecks include:
- **Path planning**: A* or Dijkstra computation
- **Costmap updates**: Processing sensor data
- **Trajectory generation**: Sampling and evaluation
- **Collision checking**: Robot shape vs obstacles

## Quality Metrics

### Success Metrics

#### Navigation Success Rate
- **Definition**: Percentage of goals reached successfully
- **Target**: >85% for reliable systems
- **Measurement**: Trials / Successful completions

#### Path Quality
- **Optimality**: How close path is to optimal
- **Smoothness**: Rate of curvature changes
- **Safety**: Distance maintained from obstacles

#### Execution Quality
- **Efficiency**: Time to reach goal
- **Stability**: Consistent velocity profiles
- **Accuracy**: Final position error

## Troubleshooting Common Issues

### Planning Failures

- **No path found**: Check map quality and goal validity
- **Suboptimal paths**: Adjust planner parameters
- **Planning timeouts**: Increase timeout values or simplify environment

### Execution Issues

- **Oscillation**: Reduce controller gains or increase tolerances
- **Getting stuck**: Improve local planner parameters
- **Collision**: Increase safety margins or reduce speeds

### Parameter Tuning

- **Start conservative**: Begin with slow speeds and large safety margins
- **Iterative improvement**: Adjust parameters gradually
- **Humanoid-specific**: Account for stability and kinematic constraints

The next section will cover the navigation workflow and implementation diagrams.