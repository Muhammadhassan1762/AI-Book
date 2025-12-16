---
sidebar_position: 2
---

# Links, Joints, and Frames

## Understanding URDF Structure for Humanoid Robots

In URDF, robots are represented as collections of **links** connected by **joints**. Understanding these fundamental components is crucial for creating accurate and functional humanoid robot models.

## Links: The Rigid Bodies of Your Robot

### What is a Link?

A **link** in URDF represents a rigid body part of the robot. It's a fundamental building block that defines:

- Physical properties (mass, inertia)
- Visual appearance (how it looks)
- Collision properties (how it interacts with the environment)
- Reference frame (coordinate system)

### Link Structure

```xml
<link name="link_name">
  <visual>
    <!-- How the link appears visually -->
  </visual>
  <collision>
    <!-- How the link interacts in collision detection -->
  </collision>
  <inertial>
    <!-- Physical properties for simulation -->
  </inertial>
</link>
```

### Link Properties

#### Visual Element
The visual element defines how the link appears in visualization and simulation:

```xml
<visual>
  <geometry>
    <!-- Shape definition: box, cylinder, sphere, mesh -->
    <box size="0.1 0.2 0.3"/>
  </geometry>
  <material name="red">
    <color rgba="1 0 0 1"/>
  </material>
  <origin xyz="0 0 0" rpy="0 0 0"/>
</visual>
```

#### Collision Element
The collision element defines how the link interacts with other objects in physics simulation:

```xml
<collision>
  <geometry>
    <!-- Often simpler than visual geometry for performance -->
    <box size="0.1 0.2 0.3"/>
  </geometry>
  <origin xyz="0 0 0" rpy="0 0 0"/>
</collision>
```

#### Inertial Element
The inertial element defines physical properties for dynamics simulation:

```xml
<inertial>
  <mass value="1.0"/>
  <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
</inertial>
```

## Joints: Connecting the Links

### What is a Joint?

A **joint** connects two links and defines how they can move relative to each other. Joints are crucial for creating articulated robots like humanoids.

### Joint Types

URDF supports several joint types:

- **revolute**: Rotational joint with limited range (like an elbow)
- **continuous**: Rotational joint without limits (like a wheel)
- **prismatic**: Linear sliding joint
- **fixed**: No movement (used for permanent connections)
- **floating**: 6 DOF with no limits
- **planar**: Movement in a plane

### Joint Structure

```xml
<joint name="joint_name" type="joint_type">
  <parent link="parent_link_name"/>
  <child link="child_link_name"/>
  <origin xyz="x y z" rpy="roll pitch yaw"/>
  <axis xyz="x y z"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

### Joint Properties Explained

- **parent/child**: Defines which links are connected
- **origin**: Position and orientation of the joint relative to the parent link
- **axis**: Direction of the joint's motion (for revolute/prismatic joints)
- **limit**: For revolute joints, defines the range of motion

## Frames: Coordinate Systems in URDF

### Understanding TF (Transforms)

In ROS 2, each link has its own coordinate frame. The **tf** (transform) system keeps track of the relationships between all these frames. This is essential for:

- Robot localization
- Sensor fusion
- Motion planning
- Visualization

### Frame Conventions

ROS 2 follows specific coordinate conventions:
- **X**: Forward
- **Y**: Left
- **Z**: Up

This is a right-handed coordinate system that's standard across ROS.

## Humanoid Robot Kinematic Structure

### Typical Humanoid Structure

A humanoid robot typically has this kinematic structure:

```
base_link (torso)
├── head
├── left_arm
│   ├── left_forearm
│   └── left_hand
├── right_arm
│   ├── right_forearm
│   └── right_hand
├── left_leg
│   ├── left_lower_leg
│   └── left_foot
└── right_leg
    ├── right_lower_leg
    └── right_foot
```

### Creating a Simple Humanoid Example

Here's a simplified example of a humanoid torso and head:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Base link (torso) -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.6"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.6"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.5" ixy="0.0" ixz="0.0" iyy="0.5" iyz="0.0" izz="0.5"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Neck joint connecting torso to head -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>  <!-- Pitch rotation -->
    <limit lower="-0.5" upper="0.5" effort="10" velocity="1"/>
  </joint>
</robot>
```

## Best Practices for Humanoid Modeling

### 1. Start Simple
Begin with a basic skeleton and add complexity gradually. This makes debugging easier.

### 2. Proper Inertial Properties
Accurate inertial properties are crucial for realistic simulation. Use simplified shapes and approximate values initially.

### 3. Consistent Naming
Use descriptive names that clearly indicate the link's purpose:
- `left_upper_arm` instead of `arm1`
- `right_foot` instead of `foot_r`

### 4. Appropriate Joint Limits
Set realistic joint limits based on human anatomy or your robot's mechanical constraints.

### 5. Mass Distribution
Ensure that masses are distributed realistically. The torso should be heavier than the limbs.

## Advanced Link and Joint Concepts

### Mimic Joints
For symmetrical robots, you can use mimic joints to copy another joint's movement:

```xml
<joint name="right_elbow_mimic" type="revolute">
  <parent link="right_upper_arm"/>
  <child link="right_lower_arm"/>
  <origin xyz="0 0 -0.3" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-2.0" upper="0.0" effort="10" velocity="1"/>
  <mimic joint="left_elbow" multiplier="1.0" offset="0.0"/>
</joint>
```

### Transmission Elements
For real robots, transmission elements define how actuators connect to joints:

```xml
<transmission name="left_elbow_trans">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_elbow">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_elbow_motor">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

## URDF Validation

### Checking URDF Validity
You can validate your URDF files using ROS 2 tools:

```bash
# Check if URDF is syntactically correct
check_urdf /path/to/robot.urdf

# View the kinematic tree
urdf_to_graphiz /path/to/robot.urdf
```

### Common Issues to Avoid
1. **Disconnected links**: Every link should be connected to the tree
2. **Inconsistent joint definitions**: Parent/child links must exist
3. **Invalid XML**: Ensure proper XML syntax and structure
4. **Zero masses**: All links should have positive mass values
5. **Improper inertial tensors**: Ensure they follow physical laws

## Summary

Links, joints, and frames form the foundation of URDF robot models. Understanding how to properly define these elements is crucial for creating functional humanoid robots. The key is to start with a simple structure and gradually add complexity while maintaining proper physical properties and kinematic relationships.

In the next section, we'll explore the important distinction between visual and collision models, which is essential for efficient simulation.