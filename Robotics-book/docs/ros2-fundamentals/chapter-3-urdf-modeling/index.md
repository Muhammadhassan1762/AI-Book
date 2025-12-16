---
sidebar_position: 1
---

# Humanoid Modeling with URDF

## Understanding Robot Description for Humanoid Robots

Unified Robot Description Format (URDF) is the standard XML-based format for representing robot models in ROS. For humanoid robots, URDF is essential for defining the physical structure, kinematic relationships, and visual/collision properties that enable simulation and control.

## Learning Objectives

By the end of this chapter, you will:
- Understand the structure and components of URDF files
- Learn to create kinematic chains for humanoid robots
- Define visual and collision models for realistic simulation
- Integrate URDF with ROS 2 systems for humanoid robot control

## What is URDF?

URDF (Unified Robot Description Format) is an XML format that describes robot models including:
- **Kinematic structure**: How links and joints connect to form the robot
- **Visual properties**: How the robot appears in simulation
- **Collision properties**: How the robot interacts with its environment
- **Physical properties**: Mass, inertia, and other physical characteristics

For humanoid robots, URDF enables:
- Accurate simulation of human-like movement
- Proper kinematic calculations for walking and manipulation
- Collision detection and avoidance
- Integration with motion planning algorithms

## URDF Structure for Humanoid Robots

A humanoid robot URDF typically follows this structure:

```
robot
├── base_link (torso/pelvis)
    ├── left_leg
    │   ├── left_hip
    │   ├── left_knee
    │   └── left_ankle
    ├── right_leg
    │   ├── right_hip
    │   ├── right_knee
    │   └── right_ankle
    ├── torso
    │   ├── head
    │   ├── left_arm
    │   │   ├── left_shoulder
    │   │   ├── left_elbow
    │   │   └── left_wrist
    │   └── right_arm
    │       ├── right_shoulder
    │       ├── right_elbow
    │       └── right_wrist
```

## Basic URDF Components

### Links
Links represent rigid bodies of the robot:

```xml
<link name="base_link">
  <inertial>
    <mass value="10.0" />
    <origin xyz="0 0 0" />
    <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0" />
  </inertial>
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0" />
    <geometry>
      <box size="0.5 0.3 0.8" />
    </geometry>
    <material name="grey">
      <color rgba="0.5 0.5 0.5 1.0" />
    </material>
  </visual>
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0" />
    <geometry>
      <box size="0.5 0.3 0.8" />
    </geometry>
  </collision>
</link>
```

### Joints
Joints connect links and define their relative motion:

```xml
<joint name="left_hip_joint" type="revolute">
  <parent link="base_link" />
  <child link="left_thigh" />
  <origin xyz="0 -0.15 -0.1" rpy="0 0 0" />
  <axis xyz="0 0 1" />
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1.0" />
</joint>
```

## Complete Humanoid URDF Example

Here's a simplified humanoid robot URDF:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Base Link -->
  <link name="base_link">
    <inertial>
      <mass value="10.0" />
      <origin xyz="0 0 0.4" />
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0" />
    </inertial>
    <visual>
      <origin xyz="0 0 0.4" />
      <geometry>
        <box size="0.3 0.3 0.8" />
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1" />
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.4" />
      <geometry>
        <box size="0.3 0.3 0.8" />
      </geometry>
    </collision>
  </link>

  <!-- Head -->
  <link name="head">
    <inertial>
      <mass value="2.0" />
      <origin xyz="0 0 0" />
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1" />
    </inertial>
    <visual>
      <origin xyz="0 0 0.15" />
      <geometry>
        <sphere radius="0.15" />
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1" />
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.15" />
      <geometry>
        <sphere radius="0.15" />
      </geometry>
    </collision>
  </link>

  <joint name="neck_joint" type="revolute">
    <parent link="base_link" />
    <child link="head" />
    <origin xyz="0 0 0.8" />
    <axis xyz="0 1 0" />
    <limit lower="-0.5" upper="0.5" effort="10" velocity="1.0" />
  </joint>

  <!-- Left Arm -->
  <link name="left_upper_arm">
    <inertial>
      <mass value="1.0" />
      <origin xyz="0 0 -0.15" />
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.01" />
    </inertial>
    <visual>
      <origin xyz="0 0 -0.15" />
      <geometry>
        <cylinder length="0.3" radius="0.05" />
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1" />
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" />
      <geometry>
        <cylinder length="0.3" radius="0.05" />
      </geometry>
    </collision>
  </link>

  <joint name="left_shoulder_joint" type="revolute">
    <parent link="base_link" />
    <child link="left_upper_arm" />
    <origin xyz="0.15 0.1 0.6" />
    <axis xyz="0 1 0" />
    <limit lower="-1.57" upper="1.57" effort="20" velocity="1.0" />
  </joint>
</robot>
```

## URDF and ROS 2 Integration

URDF integrates with ROS 2 systems through:

1. **Robot State Publisher**: Publishes transforms for visualization
2. **TF2**: Provides coordinate transformations
3. **Gazebo/Isaac Sim**: Uses URDF for physics simulation
4. **Motion Planning**: Uses kinematic structure for path planning

### Robot State Publisher Node

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math

class RobotStatePublisher(Node):
    def __init__(self):
        super().__init__('robot_state_publisher')

        # Subscribe to joint states
        self.joint_sub = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10
        )

        # Create transform broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

    def joint_state_callback(self, msg):
        """Process joint states and broadcast transforms"""
        for i, joint_name in enumerate(msg.name):
            if i < len(msg.position):
                # Create transform for this joint
                t = TransformStamped()
                t.header.stamp = self.get_clock().now().to_msg()
                t.header.frame_id = 'base_link'
                t.child_frame_id = joint_name
                t.transform.translation.x = 0.0
                t.transform.translation.y = 0.0
                t.transform.translation.z = 0.0
                t.transform.rotation.x = 0.0
                t.transform.rotation.y = 0.0
                t.transform.rotation.z = math.sin(msg.position[i] / 2.0)
                t.transform.rotation.w = math.cos(msg.position[i] / 2.0)

                self.tf_broadcaster.sendTransform(t)
```

## Visual vs Collision Models

For humanoid robots, it's important to distinguish between:

- **Visual models**: How the robot appears (for rendering)
- **Collision models**: How the robot interacts physically (for physics simulation)

Visual models can be detailed and complex, while collision models should be simplified for performance.

## Best Practices for Humanoid URDF

1. **Start simple**: Begin with basic shapes and add detail gradually
2. **Proper mass distribution**: Ensure realistic inertial properties
3. **Appropriate joint limits**: Reflect real hardware constraints
4. **Consistent naming**: Use clear, consistent link and joint names
5. **Validate with tools**: Use URDF validators and checkers
6. **Consider simulation performance**: Balance detail with performance

## Integration with Vision-Language-Action Systems

URDF models are crucial for VLA systems as they:
- Enable accurate simulation for testing voice commands
- Provide kinematic models for action planning
- Allow validation of planned actions before execution
- Enable physics-based simulation of robot-environment interactions

## Next Steps

In the following sections, we'll explore links, joints, frames in detail, and learn how to create visual and collision models for realistic humanoid robot simulation.