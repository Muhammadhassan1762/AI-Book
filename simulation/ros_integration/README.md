# ROS Integration

This directory contains ROS 2 integration components for the Digital Twin simulation system.

## Purpose

The ROS integration layer provides:

1. **Bridge Services**: Connects Gazebo physics simulation with Unity visual simulation
2. **State Synchronization**: Maintains consistency between physics and visual layers
3. **Sensor Data Handling**: Manages simulated sensor data flow
4. **Environment Management**: Controls simulation parameters and settings

## Configuration Files

- `unity_bridge.yaml`: Configuration for ROS bridge connecting to Unity
- `environment_config.yaml`: Physics and environment settings

## Launch Files

- `simulation_bridge.launch.py`: Launches all integration nodes

## ROS Node Interfaces

### Physics Simulator Node
- **Publishers**:
  - `/robot/physics/state` (nav_msgs/Odometry) - Physics-based robot state
- **Services**:
  - `/physics/reset_simulation` (std_srvs/Empty) - Reset simulation
  - `/physics/set_gravity` (gazebo_msgs/SetPhysicsProperties) - Configure gravity

### Visual Simulator Node
- **Publishers**:
  - `/robot/visual/state` (geometry_msgs/PoseStamped) - Visual-only robot state
- **Subscribers**:
  - `/robot/physics/state` (nav_msgs/Odometry) - Physics state for rendering

### Sensor Simulator Node
- **Publishers**:
  - `/laser_scan` (sensor_msgs/LaserScan) - Simulated LiDAR data
  - `/depth_camera/image_raw` (sensor_msgs/Image) - Simulated RGB image
  - `/depth_camera/depth/image_raw` (sensor_msgs/Image) - Simulated depth data
  - `/imu/data` (sensor_msgs/Imu) - Simulated IMU data

### Digital Twin Synchronizer Node
- **Publishers**:
  - `/twin/sync_status` (std_msgs/String) - Synchronization status
- **Services**:
  - `/twin/sync_now` (std_srvs/Trigger) - Force immediate synchronization

### Environment Manager Node
- **Parameters**:
  - `physics_engine` (string) - Physics engine to use
  - `gravity_vector` (list of floats) - Gravity vector in x, y, z coordinates
  - `simulation_realtime_factor` (double) - Real-time factor for simulation speed

## Usage

To launch the complete simulation system:

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash
source ~/simulation_ws/install/setup.bash

# Launch the simulation with ROS integration
ros2 launch ros_integration simulation_bridge.launch.py
```

## Architecture

The ROS integration follows a modular architecture where each component handles a specific aspect of the digital twin system:

- Physics simulation runs in Gazebo with accurate physics properties
- Visual simulation runs in Unity with high-fidelity rendering
- ROS nodes manage communication and synchronization between systems
- Sensor simulation provides realistic sensor data for the digital twin