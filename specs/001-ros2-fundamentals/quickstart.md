# Quickstart: The Robotic Nervous System (ROS 2)

## Prerequisites

- Ubuntu 22.04 LTS (recommended) or compatible Linux distribution
- Python 3.8 or higher
- ROS 2 Humble Hawksbill installed
- Docusaurus development environment (Node.js 18+)
- Gazebo Garden for simulation

## Installation Steps

### 1. Install ROS 2 Humble Hawksbill

```bash
# Add ROS 2 repository
sudo apt update && sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 packages
sudo apt update
sudo apt install ros-humble-desktop ros-humble-rclpy ros-humble-urdf ros-humble-xacro
sudo apt install python3-rosdep2 python3-rosinstall python3-rosinstall-generator python3-build
```

### 2. Setup ROS 2 Environment

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Create ROS 2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### 3. Install Simulation Environment

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

## Running Examples

### 1. Basic Publisher-Subscriber Example

```bash
# Navigate to workspace
cd ~/ros2_ws/src

# Create example package
ros2 pkg create --build-type ament_python ros2_fundamentals_examples

# Copy the example code to the package
# Then build and run
cd ~/ros2_ws
colcon build --packages-select ros2_fundamentals_examples
source install/setup.bash

# Run publisher
ros2 run ros2_fundamentals_examples publisher

# In another terminal, run subscriber
ros2 run ros2_fundamentals_examples subscriber
```

### 2. URDF Model Visualization

```bash
# Launch RViz2 with URDF model
ros2 launch urdf_tutorial display.launch.py model:=path/to/robot.urdf
```

### 3. Simulation Example

```bash
# Launch Gazebo with simple robot
ros2 launch simulation_launch.py
```

## Development Workflow

1. Create a new branch for your feature: `git checkout -b 001-ros2-fundamentals`
2. Add your ROS 2 nodes to the `src/ros-examples/python/` directory
3. Create or update URDF models in the `simulation/models/` directory
4. Add documentation in the `docs/` directory following Docusaurus format
5. Test your examples in Gazebo simulation
6. Build and serve documentation locally: `cd docs && npm run build && npm run serve`
7. Submit pull request when ready

## Troubleshooting

- **ROS 2 environment not found**: Make sure to source the setup.bash file in each new terminal
- **Python modules not found**: Ensure rclpy is installed: `pip3 install ros2launch`
- **Gazebo not launching**: Check that Gazebo Garden is properly installed and sourced
- **Documentation build errors**: Verify Node.js version is 18+ and all dependencies are installed