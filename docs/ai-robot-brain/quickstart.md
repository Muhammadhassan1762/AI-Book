---
title: AI-Robot Brain Quickstart Guide
sidebar_position: 1
---

# AI-Robot Brain Quickstart Guide

This quickstart guide will help you set up and run the complete AI-Robot Brain pipeline: Isaac Sim for synthetic data → Isaac ROS VSLAM → Nav2 navigation.

## Overview

The AI-Robot Brain module combines three key components:
1. **Isaac Sim** for synthetic data generation
2. **Isaac ROS VSLAM** for perception and mapping
3. **Nav2** for navigation planning and execution

## Prerequisites

- Ubuntu 22.04 LTS or compatible Linux distribution
- ROS 2 Humble Hawksbill installed
- NVIDIA Isaac Sim installed and licensed
- Isaac ROS packages installed
- Nav2 navigation stack installed
- Python 3.8 or higher
- NVIDIA GPU with CUDA support

## Installation Steps

### 1. Install ROS 2 and Dependencies
```bash
# Add ROS 2 repository
sudo apt update && sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 packages
sudo apt update
sudo apt install ros-humble-desktop ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install ros-humble-isaac-*  # Isaac ROS packages
sudo apt install python3-rosdep2 python3-rosinstall python3-rosinstall-generator python3-build
```

### 2. Setup ROS 2 Environment
```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Create workspace for AI-Robot Brain components
mkdir -p ~/ai_robot_ws/src
cd ~/ai_robot_ws
colcon build
source install/setup.bash
```

### 3. Install Isaac Sim and Isaac ROS
Follow the official NVIDIA Isaac Sim installation guide:
- Download and install Isaac Sim from NVIDIA Developer website
- Install Isaac ROS packages using the official documentation
- Ensure Isaac Sim is properly licensed and configured

## Running the Complete Pipeline

### 1. Synthetic Data Generation
```bash
# Source environments
source /opt/ros/humble/setup.bash
source ~/ai_robot_ws/install/setup.bash

# Launch Isaac Sim with Replicator for synthetic data generation
ros2 launch isaac_sim synthetic_data_generation.launch.py
```

### 2. VSLAM Pipeline
```bash
# In a new terminal, source environments
source /opt/ros/humble/setup.bash
source ~/ai_robot_ws/install/setup.bash

# Launch Isaac ROS VSLAM pipeline
ros2 launch isaac_ros vslam_pipeline.launch.py
```

### 3. Navigation with Nav2
```bash
# In a new terminal, source environments
source /opt/ros/humble/setup.bash
source ~/ai_robot_ws/install/setup.bash

# Launch Nav2 navigation with VSLAM input
ros2 launch nav2 navigation_pipeline.launch.py
```

## Basic Examples

### Example 1: Generate Synthetic Dataset
```bash
# Navigate to workspace
cd ~/ai_robot_ws/src

# Run the synthetic data generation script
ros2 run synthetic_data_generator generate_dataset \
  --dataset_name "training_data" \
  --num_samples 1000 \
  --enable_depth true \
  --enable_segmentation true
```

### Example 2: Run VSLAM Pipeline
```bash
# Launch VSLAM with Isaac Sim camera feed
ros2 launch vslam_bringup vslam.launch.py \
  camera_topic:=/synthetic/rgb \
  enable_loop_closure:=true
```

### Example 3: Navigate to Goal
```bash
# Send a navigation goal to Nav2
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: 'map'},
    pose: {
      position: {x: 1.0, y: 1.0, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  }
}"
```

## Development Workflow
1. Create a new branch for your feature: `git checkout -b ai-robot-brain`
2. Add your simulation configurations to the `simulation/isaac/` directory
3. Create or update launch files in the `simulation/isaac_ros/launch/` and `simulation/nav2/launch/` directories
4. Add documentation following Docusaurus format in `docs/ai-robot-brain/`
5. Test your examples in Isaac Sim environment
6. Build and serve documentation locally: `cd docs && npm run build && npm run serve`
7. Submit pull request when ready

## Validation Exercises

### Exercise 1: Synthetic Data Quality
- Generate a dataset with RGB, Depth, and Segmentation images
- Verify that images are properly synchronized
- Check that annotations are accurate and complete

### Exercise 2: VSLAM Performance
- Run the VSLAM pipeline with Isaac Sim camera feed
- Verify that pose estimation is accurate
- Check that the generated map represents the environment correctly

### Exercise 3: Navigation Success
- Use Nav2 to navigate to specified goals
- Verify that the robot avoids obstacles
- Confirm that navigation goals are reached successfully

## Troubleshooting

- **Isaac Sim not launching**: Check that Isaac Sim is properly installed and licensed
- **ROS 2 environment not found**: Make sure to source the setup.bash file in each new terminal
- **VSLAM tracking lost**: Ensure sufficient visual features in the environment
- **Navigation fails**: Verify that maps are properly generated and accessible
- **Performance issues**: Check system requirements and GPU capabilities

## Next Steps

Once you've completed this quickstart:
1. Explore the detailed chapters on each component
2. Experiment with different robot configurations
3. Customize the navigation parameters for your specific needs
4. Integrate with your own robotic platforms
5. Extend the perception and navigation capabilities

This guide provides the foundation for building more complex AI-Robot Brain applications using the Isaac ecosystem.