---
sidebar_position: 1
---

# Chapter 3: Humanoid Modeling with URDF

## Understanding Robot Description in ROS 2

Welcome to Chapter 3, where we'll explore URDF (Unified Robot Description Format), the standard way to represent robot models in ROS 2. URDF is essential for robotics as it defines the physical and visual properties of robots, enabling simulation, visualization, and control. In this chapter, we'll focus specifically on modeling humanoid robots using URDF.

### What is URDF?

URDF (Unified Robot Description Format) is an XML-based format used to describe robot models in ROS. It defines:

- **Physical structure**: Links (rigid parts) and joints (connections between links)
- **Visual appearance**: How the robot looks in simulation and visualization
- **Collision properties**: How the robot interacts with the environment in simulation
- **Inertial properties**: Mass, center of mass, and inertia for physics simulation
- **Kinematic properties**: Joint limits, types, and ranges of motion

### Why URDF Matters for Humanoid Robots

Humanoid robots present unique challenges for modeling:

- **Complex kinematic chains**: Multiple limbs with various degrees of freedom
- **Symmetry**: Arms and legs that mirror each other
- **Multiple interaction points**: Hands for manipulation, feet for locomotion
- **Balance requirements**: Center of mass considerations for stable locomotion

### Learning Objectives

By the end of this chapter, you will:

1. Understand the structure of URDF files and their XML format
2. Learn to define links, joints, and their properties for humanoid robots
3. Distinguish between visual and collision models
4. Create complete humanoid robot models with proper kinematic chains
5. Understand how URDF integrates with ROS 2 simulation and visualization tools

### Chapter Structure

This chapter is organized into the following sections:

- [Links, Joints, and Frames](./links-joints-frames.md): Understanding the basic building blocks of URDF models
- [Visual vs Collision Models](./visual-collision-models.md): Creating appropriate visual and collision representations

### Visual Overview

Here's a diagram showing the structure of a simple humanoid robot in URDF:

```
Base Link (Torso)
    |
    +-- Head (via neck joint)
    |
    +-- Left Arm
    |   |
    |   +-- Left Forearm
    |   |
    |   +-- Left Hand
    |
    +-- Right Arm
    |   |
    |   +-- Right Forearm
    |   |
    |   +-- Right Hand
    |
    +-- Left Leg
    |   |
    |   +-- Left Lower Leg
    |   |
    |   +-- Left Foot
    |
    +-- Right Leg
        |
        +-- Right Lower Leg
        |
        +-- Right Foot
```

And here's how visual and collision models relate:

```
Link: "Upper Arm"
├── Visual Model (for appearance)
│   ├── Shape: Detailed mesh
│   ├── Color: Robot gray
│   └── Texture: Metallic finish
└── Collision Model (for physics)
    ├── Shape: Simple cylinder
    ├── Size: Bounding volume
    └── Position: Same origin
```

### Prerequisites

Before starting this chapter, you should have:

- Completed Chapters 1 and 2 (ROS 2 Fundamentals and AI Integration)
- Basic understanding of XML format
- Understanding of 3D coordinate systems and transformations
- A working ROS 2 installation

The examples in this chapter will continue to use simulation-first development, allowing you to experiment with robot modeling without requiring physical hardware.

### URDF in the ROS 2 Ecosystem

URDF integrates with several key ROS 2 tools:

- **Robot State Publisher**: Publishes joint states to maintain consistent transforms
- **RViz2**: Visualizes robot models with their current joint states
- **Gazebo**: Provides physics simulation based on URDF specifications
- **MoveIt**: Uses URDF for motion planning and inverse kinematics

Let's begin exploring the fundamental components of URDF and how they come together to create realistic humanoid robot models!