---
sidebar_position: 2
---

# Quickstart Guide: ROS 2 Fundamentals

## Getting Started with ROS 2, AI Integration, and URDF Modeling

This quickstart guide will help you set up your environment and run the examples from this module. Follow these steps to get up and running quickly with ROS 2 fundamentals, AI-robot integration, and URDF modeling.

## Prerequisites

Before starting, ensure you have:

- Ubuntu 22.04 LTS (recommended) or compatible Linux distribution
- ROS 2 Humble Hawksbill installed
- Python 3.8 or higher
- Git for version control
- Basic command-line familiarity

## Installation

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

### 2. Set up ROS 2 Environment

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Create a ROS 2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Build the workspace (even though it's empty initially)
colcon build
source install/setup.bash
```

## Running the Examples

### Example 1: Basic Publisher-Subscriber

This example demonstrates the fundamental ROS 2 communication pattern.

1. **Run the publisher**:
```bash
# Terminal 1
ros2 run ros2_fundamentals_examples basic_publisher
```

2. **Run the subscriber** (in a new terminal):
```bash
# Terminal 2
source ~/ros2_ws/install/setup.bash  # Source workspace
ros2 run ros2_fundamentals_examples basic_subscriber
```

3. **Expected output**:
   - Publisher terminal: "Publishing: 'Hello World: X'" (every 0.5 seconds)
   - Subscriber terminal: "I heard: 'Hello World: X'" (receiving published messages)

### Example 2: AI-Robot Integration

This example shows how AI decision-making connects to robot control.

1. **Run the AI decision node**:
```bash
# Terminal 1
ros2 run ros2_fundamentals_examples ai_decision_node
```

2. **Run the robot controller** (in a new terminal):
```bash
# Terminal 2
ros2 run ros2_fundamentals_examples robot_controller
```

3. **Monitor the system** (in a third terminal):
```bash
# Terminal 3
# Monitor commands sent to robot
ros2 topic echo robot_cmd_vel geometry_msgs/msg/Twist

# Or monitor robot status
ros2 topic echo robot_status std_msgs/msg/String
```

### Example 3: URDF Model Visualization

This example demonstrates loading and visualizing a robot model.

1. **Launch RViz2 with the humanoid model**:
```bash
# Method 1: Using the launch file
ros2 launch simulation_launch urdf_visualization.launch.py

# Method 2: Manual launch
# Terminal 1: Publish robot description
ros2 run ros2_fundamentals_examples urdf_parser

# Terminal 2: Launch RViz2
ros2 run rviz2 rviz2
```

2. **In RViz2**:
   - Add a RobotModel display
   - Set the Robot Description to "robot_description"
   - You should see the simple humanoid model

## Understanding the Code Structure

### Python Nodes Location
All Python examples are in the `src/ros-examples/` directory:
- `basic_publisher.py` - Simple publisher example
- `basic_subscriber.py` - Simple subscriber example
- `ai_decision_node.py` - AI decision-making example
- `robot_controller.py` - Robot control interface
- `urdf_parser.py` - URDF parsing example

### URDF Model Location
The humanoid robot model is in `simulation/models/simple_humanoid/model.urdf`

### Launch Files Location
Launch files are in `simulation/launch/`:
- `publisher_subscriber.launch.py` - Launch publisher and subscriber together
- `ai_robot_integration.launch.py` - Launch AI and controller together
- `urdf_visualization.launch.py` - Launch visualization

## Launching Multiple Examples Together

You can run multiple examples simultaneously using launch files:

```bash
# Launch publisher and subscriber together
ros2 launch simulation_launch publisher_subscriber.launch.py

# Launch AI-robot integration
ros2 launch simulation_launch ai_robot_integration.launch.py
```

## Monitoring and Debugging

### Useful ROS 2 Commands

```bash
# List all active topics
ros2 topic list

# Echo messages on a specific topic
ros2 topic echo /chatter std_msgs/msg/String

# List all active nodes
ros2 node list

# Show the graph of nodes and topics
ros2 run rqt_graph rqt_graph

# Check the type of a topic
ros2 topic info /chatter

# Publish a message to a topic (for testing)
ros2 topic pub /chatter std_msgs/String "data: 'Test message'"
```

## Simulation Environment

If you have Gazebo installed, you can also run the examples in simulation:

```bash
# Install Gazebo if not already installed
sudo apt install ros-humble-gazebo-ros ros-humble-gazebo-plugins

# Launch with Gazebo
# (Note: This requires additional configuration for our examples)
```

## Troubleshooting

### Common Issues and Solutions

1. **"Command 'ros2' not found"**
   - Make sure ROS 2 is installed and sourced
   - Run: `source /opt/ros/humble/setup.bash`

2. **"Module not found" errors**
   - Make sure your workspace is built and sourced
   - Run: `cd ~/ros2_ws && colcon build && source install/setup.bash`

3. **"Topic not found" errors**
   - Ensure the publisher node is running before the subscriber
   - Check topic names match exactly

4. **Python import errors**
   - Ensure you're using Python 3.8+
   - Make sure your workspace is sourced

## Next Steps

Now that you've run the basic examples, try:

1. **Modifying the examples**: Change parameters, message content, or behavior
2. **Creating your own nodes**: Use `rclpy_template.py` as a starting point
3. **Expanding the URDF model**: Add more links and joints to the humanoid model
4. **Enhancing the AI**: Improve the decision-making logic in the AI node
5. **Reading the detailed chapters**: Dive deeper into each topic in the following sections

## Testing the Complete Workflow

Now that you've learned about all three components (ROS 2 fundamentals, AI integration, and URDF modeling), let's test them all together in a complete example:

1. **Launch the complete simulation environment**:
```bash
# Terminal 1: Launch Gazebo with the complete world
# (This requires Gazebo installation)
# ros2 launch gazebo_ros gazebo.launch.py world:=path/to/ros2_fundamentals.world
```

2. **Run the AI navigation system with URDF visualization**:
```bash
# Terminal 1: Start the URDF parser to publish robot description
ros2 run ros2_fundamentals_examples urdf_parser

# Terminal 2: Start the AI decision node
ros2 run ros2_fundamentals_examples ai_decision_node

# Terminal 3: Start the robot controller
ros2 run ros2_fundamentals_examples robot_controller

# Terminal 4: Start RViz2 to visualize the robot
ros2 run rviz2 rviz2
```

3. **Monitor the integrated system**:
```bash
# In additional terminals, monitor different aspects:
# Monitor robot commands
ros2 topic echo /robot_cmd_vel geometry_msgs/msg/Twist

# Monitor robot status
ros2 topic echo /robot_status std_msgs/msg/String

# Monitor sensor data
ros2 topic echo /sensor_data std_msgs/msg/String

# Visualize the TF tree
ros2 run tf2_tools view_frames
```

## Summary

This quickstart guide provided:
- Environment setup for ROS 2 development
- Running the fundamental examples (publisher-subscriber)
- Running the AI-robot integration example
- Visualizing URDF models
- Basic monitoring and debugging techniques
- Integration of all components in a complete workflow

You're now ready to explore the detailed concepts in the following chapters!