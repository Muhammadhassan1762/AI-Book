---
sidebar_position: 2
---

# Links, Joints, and Frames

## Building the Kinematic Structure of Humanoid Robots

Understanding links, joints, and frames is fundamental to creating accurate URDF models for humanoid robots. These elements define the physical structure, kinematic relationships, and coordinate systems that enable proper robot simulation and control.

## Links: The Building Blocks

Links represent rigid bodies in the robot. Each link has:

- **Physical properties**: Mass, center of mass, and inertia
- **Visual properties**: How the link appears in simulation
- **Collision properties**: How the link interacts with the environment

### Link Properties for Humanoid Robots

For humanoid robots, links typically represent body parts:

- **base_link**: The main body/torso, often the pelvis for bipeds
- **head**: The skull with sensors (cameras, microphones)
- **limbs**: Arms and legs with appropriate segments
- **end effectors**: Hands and feet

### Link Definition Structure

```xml
<link name="link_name">
  <!-- Physical properties for simulation -->
  <inertial>
    <mass value="1.0" />
    <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />
    <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01" />
  </inertial>

  <!-- Visual representation -->
  <visual>
    <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />
    <geometry>
      <!-- Shape definition -->
    </geometry>
    <material name="material_name" />
  </visual>

  <!-- Collision detection -->
  <collision>
    <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />
    <geometry>
      <!-- Shape definition -->
    </geometry>
  </collision>
</link>
```

### Example: Humanoid Leg Link

```xml
<link name="left_thigh">
  <inertial>
    <mass value="3.0" />
    <origin xyz="0.0 0.0 -0.2" />
    <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.02" />
  </inertial>
  <visual>
    <origin xyz="0.0 0.0 -0.2" />
    <geometry>
      <cylinder length="0.4" radius="0.08" />
    </geometry>
    <material name="skin">
      <color rgba="0.8 0.6 0.4 1.0" />
    </material>
  </visual>
  <collision>
    <origin xyz="0.0 0.0 -0.2" />
    <geometry>
      <cylinder length="0.4" radius="0.08" />
    </geometry>
  </collision>
</link>
```

## Joints: The Connections

Joints define how links connect and move relative to each other. For humanoid robots, the most common joint types are:

### Joint Types

1. **Revolute**: Rotational joint with limited range (like human joints)
2. **Continuous**: Rotational joint without limits (like a wheel)
3. **Prismatic**: Linear sliding joint
4. **Fixed**: No movement (welded connection)
5. **Floating**: 6DOF movement (for base when not on ground)

### Joint Definition Structure

```xml
<joint name="joint_name" type="joint_type">
  <parent link="parent_link_name" />
  <child link="child_link_name" />
  <origin xyz="x y z" rpy="roll pitch yaw" />
  <axis xyz="x y z" />
  <limit lower="min" upper="max" effort="max_effort" velocity="max_velocity" />
  <dynamics damping="damping_value" friction="friction_value" />
</joint>
```

### Example: Humanoid Hip Joint

```xml
<joint name="left_hip_yaw" type="revolute">
  <parent link="base_link" />
  <child link="left_thigh" />
  <origin xyz="0.0 -0.1 -0.05" rpy="0 0 0" />
  <axis xyz="0 0 1" />
  <limit lower="-0.5" upper="0.5" effort="100" velocity="2.0" />
  <dynamics damping="1.0" friction="0.1" />
</joint>

<joint name="left_hip_roll" type="revolute">
  <parent link="left_thigh" />
  <child link="left_shin" />
  <origin xyz="0.0 0.0 -0.4" rpy="0 0 0" />
  <axis xyz="1 0 0" />
  <limit lower="-0.4" upper="0.4" effort="100" velocity="2.0" />
  <dynamics damping="1.0" friction="0.1" />
</joint>
```

## Complete Humanoid Joint Chain Example

Here's a complete leg kinematic chain:

```xml
<!-- Thigh -->
<link name="left_thigh">
  <inertial>
    <mass value="3.0" />
    <origin xyz="0.0 0.0 -0.2" />
    <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.02" />
  </inertial>
  <visual>
    <origin xyz="0.0 0.0 -0.2" />
    <geometry>
      <cylinder length="0.4" radius="0.08" />
    </geometry>
    <material name="skin">
      <color rgba="0.8 0.6 0.4 1.0" />
    </material>
  </visual>
  <collision>
    <origin xyz="0.0 0.0 -0.2" />
    <geometry>
      <cylinder length="0.4" radius="0.08" />
    </geometry>
  </collision>
</link>

<!-- Knee joint -->
<joint name="left_knee" type="revolute">
  <parent link="left_thigh" />
  <child link="left_shin" />
  <origin xyz="0.0 0.0 -0.4" />
  <axis xyz="0 1 0" />
  <limit lower="0.0" upper="2.5" effort="100" velocity="2.0" />
  <dynamics damping="1.0" friction="0.1" />
</joint>

<!-- Shin -->
<link name="left_shin">
  <inertial>
    <mass value="2.5" />
    <origin xyz="0.0 0.0 -0.2" />
    <inertia ixx="0.08" ixy="0.0" ixz="0.0" iyy="0.08" iyz="0.0" izz="0.015" />
  </inertial>
  <visual>
    <origin xyz="0.0 0.0 -0.2" />
    <geometry>
      <cylinder length="0.4" radius="0.07" />
    </geometry>
    <material name="skin">
      <color rgba="0.8 0.6 0.4 1.0" />
    </material>
  </visual>
  <collision>
    <origin xyz="0.0 0.0 -0.2" />
    <geometry>
      <cylinder length="0.4" radius="0.07" />
    </geometry>
  </collision>
</link>

<!-- Ankle joint -->
<joint name="left_ankle" type="revolute">
  <parent link="left_shin" />
  <child link="left_foot" />
  <origin xyz="0.0 0.0 -0.4" />
  <axis xyz="0 1 0" />
  <limit lower="-0.5" upper="0.5" effort="50" velocity="1.5" />
  <dynamics damping="0.8" friction="0.1" />
</joint>

<!-- Foot -->
<link name="left_foot">
  <inertial>
    <mass value="1.0" />
    <origin xyz="0.1 0.0 -0.05" />
    <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.03" iyz="0.0" izz="0.01" />
  </inertial>
  <visual>
    <origin xyz="0.1 0.0 -0.05" />
    <geometry>
      <box size="0.25 0.15 0.1" />
    </geometry>
    <material name="black">
      <color rgba="0.1 0.1 0.1 1.0" />
    </material>
  </visual>
  <collision>
    <origin xyz="0.1 0.0 -0.05" />
    <geometry>
      <box size="0.25 0.15 0.1" />
    </geometry>
  </collision>
</link>
```

## Frames and Coordinate Systems

Each link establishes a coordinate frame. Understanding frames is crucial for:

- **Kinematic calculations**: Forward and inverse kinematics
- **Sensor integration**: Proper sensor placement and orientation
- **Control algorithms**: End-effector positioning
- **Navigation**: Robot localization and mapping

### Frame Conventions

- **Right-hand rule**: X forward, Y left, Z up (for humanoid robots)
- **Joint axes**: Define the direction of motion
- **Origin placement**: Typically at the joint center or geometric center

### TF (Transform) Trees

The joint structure creates a tree of transforms that ROS 2's TF2 system uses:

```
map
└── odom
    └── base_link (torso)
        ├── head
        ├── left_shoulder
        │   ├── left_elbow
        │   └── left_wrist
        ├── right_shoulder
        │   ├── right_elbow
        │   └── right_wrist
        ├── left_hip
        │   ├── left_knee
        │   └── left_ankle
        └── right_hip
            ├── right_knee
            └── right_ankle
```

## Special Considerations for Humanoid Robots

### Floating Base
Humanoid robots often have a floating base (6DOF) when not in contact with ground:

```xml
<joint name="base_joint" type="floating">
  <parent link="world" />
  <child link="base_link" />
</joint>
```

### Mimic Joints
For symmetric movements (like both arms moving together):

```xml
<joint name="right_elbow" type="revolute">
  <parent link="right_upper_arm" />
  <child link="right_lower_arm" />
  <origin xyz="0 0 -0.3" />
  <axis xyz="0 1 0" />
  <limit lower="-2.0" upper="0.0" effort="50" velocity="1.0" />
  <mimic joint="left_elbow" multiplier="1.0" offset="0.0" />
</joint>
```

### Transmission Elements
Define how actuators connect to joints:

```xml
<transmission name="left_elbow_trans">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_elbow">
    <hardwareInterface>PositionJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_elbow_motor">
    <hardwareInterface>PositionJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

## Validation and Debugging

### Checking Kinematic Chains
- Ensure all links are connected
- Verify joint limits are appropriate
- Check that the model is not over-constrained

### Visualization Tools
- Use RViz to visualize the robot model
- Check TF trees with `ros2 run tf2_tools view_frames`
- Validate URDF with `check_urdf` command

## Best Practices

1. **Plan the kinematic structure** before implementation
2. **Use appropriate joint limits** that reflect human capabilities
3. **Define proper inertial properties** for stable simulation
4. **Test with kinematic solvers** to ensure reachability
5. **Consider computational complexity** when designing chains
6. **Document the frame conventions** used in your model

## Integration with ROS 2 Systems

The link-joint-frame structure enables:
- **Robot State Publisher**: Broadcasts transforms for visualization
- **Kinematics solvers**: Inverse kinematics for manipulation
- **Motion planning**: Path planning considering kinematic constraints
- **Sensor fusion**: Proper integration of sensor data in robot frames

This foundation enables the complex movements and interactions required for humanoid robots in VLA systems, where voice commands must be translated to precise physical actions through the robot's kinematic structure.