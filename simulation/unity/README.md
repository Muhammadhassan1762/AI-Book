# Unity Simulation Environment

This directory contains the Unity-based visual simulation components for the Digital Twin system.

## Project Structure

```
Assets/
├── Scenes/           # Unity scene files
│   └── humanoid_scene.unity
├── Scripts/          # C# scripts for robot control and visualization
│   └── RobotVisualController.cs
├── Materials/        # Material definitions
│   └── RobotMaterial.mat
├── Models/           # 3D model assets
├── Prefabs/          # Reusable game object templates
└── Textures/         # Texture images
```

## Purpose

This Unity project provides:

1. **Visual Simulation**: High-fidelity rendering of robots and environments
2. **Human-Robot Interaction**: Intuitive interfaces for user interaction
3. **ROS Integration**: Bridge to connect with ROS/Gazebo physics simulation
4. **Real-time Visualization**: Live visualization of robot state and sensor data

## Getting Started

1. Open this project in Unity 2022.3 LTS or later
2. Load the `humanoid_scene.unity` scene
3. Configure the ROS bridge connection settings in the RobotVisualController
4. Run the scene to visualize the robot

## Integration with Gazebo

The Unity visual simulation is designed to work in parallel with Gazebo physics simulation:
- Gazebo handles accurate physics simulation
- Unity provides high-fidelity visual rendering
- ROS bridge synchronizes state between both systems