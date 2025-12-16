---
title: Navigation Workflow and Diagrams
sidebar_position: 3
---

# Navigation Workflow and Diagrams

This section provides detailed diagrams and workflow explanations for the navigation planning process using Nav2, including implementation details and visualization of the complete navigation pipeline.

## Navigation System Workflow

The complete navigation workflow consists of several interconnected stages:

### 1. Initialization Phase
```
[Robot Startup] → [Map Loading] → [Localization Setup] → [Ready for Navigation]
```

During initialization:
- Load map from file or VSLAM system
- Initialize localization (AMCL)
- Configure costmaps
- Establish TF transforms
- Verify sensor availability

### 2. Goal Setting Phase
```
[Goal Received] → [Goal Validation] → [Path Planning Request] → [Plan Generated]
```

When a navigation goal is received:
- Validate goal is in traversable area
- Check for clear path to goal
- Plan global path from current position to goal
- Generate local trajectory to follow

### 3. Execution Phase
```
[Follow Path] → [Obstacle Detection] → [Local Replanning] → [Goal Check] → [Repeat or Complete]
```

During navigation execution:
- Follow planned path using local planner
- Continuously monitor for obstacles
- Replan local trajectory as needed
- Check if goal has been reached
- Repeat until goal achieved or failure

## System Architecture Diagrams

### High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Perception    │───▶│   Navigation     │───▶│   Robot         │
│   (VSLAM)       │    │   (Nav2)         │    │   Platform      │
│                 │    │                  │    │                 │
│ • Map Generation│    │ • Global Planner │    │ • Motion Control│
│ • Pose Estimation│   │ • Local Planner  │    │ • Trajectory    │
│ • Feature Tracking│  │ • Controller     │    │   Execution     │
└─────────────────┘    │ • Costmaps       │    └─────────────────┘
                       │ • Behavior Trees │
                       └──────────────────┘
```

### Component Interaction
```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   Sensors   │───▶│  Costmap 2D     │───▶│ Global Plan │
│             │    │                 │    │             │
│ • LaserScan │    │ • Static Layer  │    │ • A*        │
│ • IMU       │    │ • Obstacle Layer│    │ • NavFn     │
│ • Odometry  │    │ • Inflation     │    │ • Dijkstra  │
└─────────────┘    └─────────────────┘    └─────────────┘
                         │                       │
                         ▼                       ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│ Local Plan  │◀───│  Behavior Tree  │───▶│ Controller  │
│             │    │                 │    │             │
│ • DWA       │    │ • NavigateToPose│    │ • Pure Pursuit│
│ • Trajectory│    │ • FollowPath    │    │ • Regulated │
│ • Sampling  │    │ • Recovery      │    │   Pursuit   │
└─────────────┘    └─────────────────┘    └─────────────┘
```

## Navigation Pipeline Stages

### Stage 1: Map and Localization
```
┌─────────────────────────────────────────────────────────┐
│                    MAP & LOCALIZATION                   │
├─────────────────────────────────────────────────────────┤
│ Input: Map from VSLAM                                   │
│ Process: AMCL (Adaptive Monte Carlo Localization)       │
│ Output: Accurate robot pose in map frame                │
└─────────────────────────────────────────────────────────┘
```

Key components:
- **Map Server**: Provides static map data
- **AMCL**: Estimates robot pose using particle filter
- **Transforms**: Maintains coordinate frame relationships

### Stage 2: Global Path Planning
```
┌─────────────────────────────────────────────────────────┐
│                 GLOBAL PATH PLANNING                    │
├─────────────────────────────────────────────────────────┤
│ Input: Start pose, Goal pose, Map                       │
│ Process: A*/NavFn path planning algorithm               │
│ Output: Sequence of waypoints to goal                   │
└─────────────────────────────────────────────────────────┘
```

Key components:
- **Path Planner**: Computes optimal path from start to goal
- **Costmap**: Provides traversability information
- **Smoothing**: Reduces path sharp turns

### Stage 3: Local Trajectory Planning
```
┌─────────────────────────────────────────────────────────┐
│                LOCAL TRAJECTORY PLANNING                │
├─────────────────────────────────────────────────────────┤
│ Input: Global path, Current pose, Sensor data           │
│ Process: Dynamic Window Approach (DWA)                  │
│ Output: Feasible trajectory to follow                   │
└─────────────────────────────────────────────────────────┘
```

Key components:
- **Local Planner**: Generates short-term trajectories
- **Obstacle Avoidance**: Responds to dynamic obstacles
- **Kinematic Constraints**: Respects robot dynamics

### Stage 4: Motion Control
```
┌─────────────────────────────────────────────────────────┐
│                    MOTION CONTROL                       │
├─────────────────────────────────────────────────────────┤
│ Input: Desired trajectory, Current state                │
│ Process: Pure pursuit / PID control                     │
│ Output: Velocity commands to robot base                 │
└─────────────────────────────────────────────────────────┘
```

Key components:
- **Controller**: Tracks desired trajectory
- **Velocity Smoother**: Limits acceleration/jerk
- **Safety Monitor**: Emergency stop capability

## Behavior Tree Visualization

### Navigation Behavior Tree
```
NavigateToPose
├── ComputePathToPose
│   ├── IsGoalReached? (condition)
│   ├── IsValidGoal? (condition)
│   └── ComputePath (action)
├── FollowPath
│   ├── IsPathValid? (condition)
│   ├── IsGoalReached? (condition)
│   ├── IsStuck? (condition)
│   ├── FollowWaypoints (action)
│   │   ├── IsLocalPathValid? (condition)
│   │   ├── IsGoalReached? (condition)
│   │   ├── ComputeVelocityCommands (action)
│   │   └── PublishVelocity (action)
│   └── IsGoalReached? (condition)
└── Recovery
    ├── IsRecoveryEnabled? (condition)
    ├── RecoveryNodeSequence
    │   ├── Spin (action)
    │   ├── IsActionSuccessful? (condition)
    │   ├── BackUp (action)
    │   ├── IsActionSuccessful? (condition)
    │   └── Wait (action)
    └── IsActionSuccessful? (condition)
```

### Recovery Behaviors
```
Recovery Behaviors:
├── Spin
│   ├── Rotate robot in place to clear sensor view
│   └── Duration: 5-30 seconds depending on situation
├── BackUp
│   ├── Move robot backward to clear obstacle
│   └── Distance: 0.1-0.5 meters
└── Wait
    ├── Pause navigation temporarily
    └── Duration: 1-10 seconds
```

## Humanoid Navigation Specifics

### Humanoid-Specific Navigation Pipeline
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ VSLAM Map       │───▶│ Humanoid Nav2    │───▶│ Humanoid Robot  │
│ (Perception)    │    │ (Navigation)     │    │ (Execution)     │
│ • Occupancy Grid│    │ • Global Planner │    │ • Step Planner  │
│ • Localization  │    │ • Local Planner  │    │ • Balance Ctrl  │
│ • Obstacles     │    │ • Costmaps       │    │ • Foot Placement│
└─────────────────┘    │ • Recovery       │    └─────────────────┘
                       │ • Humanoid Config│
                       └──────────────────┘
```

### Humanoid Navigation Parameters
```
Humanoid-Specific Parameters:
├── Movement Constraints
│   ├── Max walking speed: 0.3 m/s (slower for stability)
│   ├── Max angular speed: 0.6 rad/s (controlled turns)
│   ├── Step size limit: 0.2 m (foot placement constraints)
│   └── Turning radius: 0.4 m (minimum turning radius)
├── Safety Margins
│   ├── Robot radius: 0.3 m (larger safety buffer)
│   ├── Inflation radius: 0.7 m (increased obstacle margin)
│   └── Cost scaling factor: 4.0 (higher obstacle costs)
└── Stability Considerations
    ├── Lookahead distance: 0.4 m (shorter planning horizon)
    ├── Path smoothing: Enabled (smooth trajectory for balance)
    └── Recovery behaviors: Conservative (safe failure modes)
```

## Data Flow Diagrams

### Real-Time Navigation Data Flow
```
Sensor Data (LaserScan, Odometry, IMU)
         ↓
    Costmap Updates
         ↓
Current Pose (AMCL)
         ↓
Global Path (A*/NavFn)
         ↓
Local Trajectory (DWA)
         ↓
Velocity Commands
         ↓
Robot Motion
         ↓
Updated Sensor Data (feedback loop)
```

### TF Tree for Navigation
```
map (static map origin)
├── odom (odometry frame)
    └── base_link (robot base)
        ├── base_footprint (projection of robot on ground)
        ├── laser_frame (for obstacle detection)
        ├── camera_frame (for VSLAM integration)
        └── imu_frame (for orientation data)
```

## Error Handling and Recovery

### Navigation Error States
```
Navigation States:
├── IDLE: Waiting for goal
├── PLANNING: Computing path to goal
├── CONTROLLING: Following trajectory
├── EXECUTING: Active navigation
├── RECOVERING: Executing recovery behavior
├── FAILED: Navigation failed permanently
└── SUCCEEDED: Goal reached successfully
```

### Recovery Flow
```
Obstacle Detected
         ↓
Is Obstacle Temporary?
         ├─ YES ─┐
         │       ↓
         │   Local Replanning
         │       ↓
         │   Continue Navigation
         │
         └─ NO ──┐
                 ↓
         Is Goal Still Valid?
                 ├─ YES ─┐
                 │       ↓
                 │   Recovery Behavior
                 │       ↓
                 │   Retry Navigation
                 │
                 └─ NO ──┐
                         ↓
                 Cancel Navigation
```

## Performance Monitoring

### Navigation Metrics Dashboard
```
Navigation Performance Metrics:
├── Success Rate: 85% (17/20 trials successful)
├── Average Time: 45s (goal reached in 45 seconds)
├── Path Efficiency: 1.2× (actual vs optimal distance)
├── Obstacle Encounters: 3 per navigation
├── Recovery Activations: 1 per navigation
└── Safety Violations: 0 (no collisions or falls)
```

This completes the navigation workflow diagrams and implementation details. The next section would cover testing and validation of the navigation system.