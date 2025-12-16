# Quickstart: The Digital Twin (Gazebo & Unity)

## Prerequisites

- Ubuntu 22.04 LTS (recommended) or compatible Linux distribution
- ROS 2 Humble Hawksbill installed
- Gazebo Garden for physics simulation
- Unity 2022.3 LTS for visual simulation
- Python 3.8 or higher
- Docusaurus development environment (Node.js 18+)
- Git for version control

## Installation Steps

### 1. Install ROS 2 and Gazebo

```bash
# Add ROS 2 repository
sudo apt update && sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 packages
sudo apt update
sudo apt install ros-humble-desktop ros-humble-gazebo-ros ros-humble-gazebo-plugins
sudo apt install python3-rosdep2 python3-rosinstall python3-rosinstall-generator python3-build
```

### 2. Setup ROS 2 Environment

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Create ROS 2 workspace for simulation components
mkdir -p ~/simulation_ws/src
cd ~/simulation_ws
colcon build
source install/setup.bash
```

### 3. Install Gazebo Garden

```bash
# Install Gazebo Garden
sudo apt install ros-humble-gazebo-ros ros-humble-gazebo-plugins ros-humble-gazebo-dev
sudo apt install gazebo
```

### 4. Install Documentation Environment

```bash
# Install Node.js and npm (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docusaurus dependencies
cd docs  # Assuming docs directory exists in your project
npm install
```

## Running Physics Simulation (Gazebo)

### 1. Basic Physics World

```bash
# Navigate to simulation workspace
cd ~/simulation_ws/src

# Launch basic physics simulation
ros2 launch simulation_launch physics_demo.launch.py
```

### 2. Humanoid Robot in Physics Environment

```bash
# Launch humanoid robot in physics world
ros2 launch simulation_launch humanoid_validation.launch.py
```

### 3. Sensor Validation Simulation

```bash
# Launch simulation with sensors for validation
ros2 launch simulation_launch sensor_validation.launch.py
```

## Unity Visual Simulation Setup

Unity simulation requires additional setup:

1. Download and install Unity Hub
2. Install Unity 2022.3 LTS through Unity Hub
3. Import the provided Unity project from `simulation/unity/`
4. Install required packages (ROS# for Unity communication)
5. Build and run the Unity scene for visual simulation

## Simulation Bridge (ROS 2 Connection)

### 1. Connecting Gazebo and Visualization

```bash
# Launch the ROS bridge between Gazebo and external visualization
source /opt/ros/humble/setup.bash
source ~/simulation_ws/install/setup.bash

# Launch bridge configuration
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

### 2. Robot State Visualization

```bash
# Visualize robot states from Gazebo simulation
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:='$(cat /path/to/robot.urdf)'
```

## Testing Sensor Simulation

### 1. LiDAR Sensor Test

```bash
# View LiDAR data from simulation
ros2 topic echo /laser_scan sensor_msgs/msg/LaserScan
```

### 2. Depth Camera Test

```bash
# View depth camera data
ros2 topic echo /depth_camera/image_raw sensor_msgs/msg/Image
ros2 topic echo /depth_camera/depth/image_raw sensor_msgs/msg/Image
```

### 3. IMU Sensor Test

```bash
# View IMU data
ros2 topic echo /imu/data sensor_msgs/msg/Imu
```

## Development Workflow

1. Create a new branch for your feature: `git checkout -b 002-digital-twin`
2. Add your simulation configurations to the `simulation/gazebo/` directory
3. Create or update Unity scenes in the `simulation/unity/` directory
4. Add documentation in the `docs/digital-twin/` directory following Docusaurus format
5. Test your simulation examples in both Gazebo and Unity environments
6. Build and serve documentation locally: `cd docs && npm run build && npm run serve`
7. Submit pull request when ready

## Validation Exercises

### Exercise 1: Physics Validation
- Compare simulated gravity effects with expected 9.81 m/s² acceleration
- Validate collision detection by testing robot interactions with environment
- Check that robot mass properties result in realistic movement

### Exercise 2: Sensor Noise Analysis
- Analyze LiDAR data for realistic noise patterns
- Validate IMU drift characteristics over time
- Compare depth camera noise to real sensor specifications

### Exercise 3: Digital Twin Synchronization
- Verify that visual and physics representations stay synchronized
- Test the bridge communication latency under different conditions
- Validate that sensor data corresponds between environments

## Troubleshooting

- **Gazebo not launching**: Check that Gazebo Garden is properly installed and sourced
- **ROS 2 environment not found**: Make sure to source the setup.bash file in each new terminal
- **Unity build errors**: Verify Unity 2022.3 LTS is installed and required packages are imported
- **Sensor topics not found**: Ensure the simulation is running and topics are being published
- **Documentation build errors**: Verify Node.js version is 18+ and all dependencies are installed