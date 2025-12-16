---
sidebar_position: 2
---

# Gravity, Collisions, and Environments

## Creating Realistic Physics for Humanoid Robot Simulation

Understanding and properly configuring gravity, collision detection, and environmental physics is crucial for creating realistic digital twins of humanoid robots. These elements determine how robots interact with their world and respond to external forces.

## Gravity Modeling for Humanoid Robots

### Standard Earth Gravity Configuration

For humanoid robots, accurate gravity modeling is essential for realistic locomotion and balance:

```xml
<world name="humanoid_physics_world">
  <!-- Standard Earth gravity -->
  <gravity>0 0 -9.8</gravity>

  <!-- Physics engine configuration -->
  <physics type="ode">
    <max_step_size>0.001</max_step_size>      <!-- Small steps for stability -->
    <real_time_factor>1.0</real_time_factor>  <!-- Real-time simulation -->
    <real_time_update_rate>1000</real_time_update_rate>
    <gravity>0 0 -9.8</gravity>

    <ode>
      <solver>
        <type>quick</type>  <!-- Fast, stable solver -->
        <iters>50</iters>   <!-- More iterations for humanoid stability -->
        <sor>1.3</sor>
      </solver>
      <constraints>
        <cfm>0.000001</cfm>  <!-- Small constraint force mixing -->
        <erp>0.2</erp>       <!-- Error reduction parameter -->
        <contact_max_correcting_vel>100</contact_max_correcting_vel>
        <contact_surface_layer>0.001</contact_surface_layer>
      </constraints>
    </ode>
  </physics>
</world>
```

### Custom Gravity Scenarios

For testing VLA systems under different conditions:

```xml
<!-- Low gravity for testing movement -->
<world name="low_gravity">
  <gravity>0 0 -1.62</gravity>  <!-- Moon gravity -->
  <!-- ... rest of configuration -->
</world>

<!-- Zero gravity for testing upper body manipulation -->
<world name="zero_gravity">
  <gravity>0 0 0</gravity>
  <!-- ... rest of configuration -->
</world>

<!-- Variable gravity for testing robustness -->
<world name="variable_gravity">
  <gravity>0 0 -12.0</gravity>  <!-- Higher than Earth -->
  <!-- ... rest of configuration -->
</world>
```

## Collision Detection and Response

### Collision Geometry Optimization

For humanoid robots, collision geometry must balance accuracy with performance:

```xml
<!-- Head collision - spherical approximation -->
<link name="head">
  <collision>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.16"/>  <!-- Slightly larger than visual -->
    </geometry>
    <surface>
      <friction>
        <ode>
          <mu>0.5</mu>
          <mu2>0.5</mu2>
        </ode>
      </friction>
      <bounce>
        <restitution_coefficient>0.1</restitution_coefficient>
        <threshold>100000</threshold>
      </bounce>
    </surface>
  </collision>
</link>

<!-- Limb collision - cylindrical approximation -->
<link name="left_upper_arm">
  <collision>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <geometry>
      <cylinder length="0.3" radius="0.06"/>  <!-- Slightly larger -->
    </geometry>
    <surface>
      <friction>
        <ode>
          <mu>0.6</mu>
          <mu2>0.6</mu2>
        </ode>
      </friction>
    </surface>
  </collision>
</link>

<!-- Foot collision - box for stability -->
<link name="left_foot">
  <collision>
    <origin xyz="0.1 0 -0.01" rpy="0 0 0"/>
    <geometry>
      <box size="0.25 0.15 0.02"/>  <!-- Foot contact area -->
    </geometry>
    <surface>
      <friction>
        <ode>
          <mu>0.9</mu>  <!-- High friction for walking stability -->
          <mu2>0.9</mu2>
        </ode>
      </friction>
      <contact>
        <ode>
          <kp>1000000</kp>  <!-- High stiffness for contact -->
          <kd>100</kd>
          <max_vel>100</max_vel>
          <min_depth>0.001</min_depth>
        </ode>
      </contact>
    </surface>
  </collision>
</link>
```

### Multi-Element Collision Models

For complex shapes, use multiple collision elements:

```xml
<link name="torso">
  <!-- Main body collision -->
  <collision name="torso_main">
    <origin xyz="0 0 0.4" rpy="0 0 0"/>
    <geometry>
      <box size="0.3 0.3 0.8"/>
    </geometry>
  </collision>

  <!-- Neck collision -->
  <collision name="neck">
    <origin xyz="0 0 0.85" rpy="0 0 0"/>
    <geometry>
      <cylinder length="0.1" radius="0.08"/>
    </geometry>
  </collision>

  <!-- Shoulders collision -->
  <collision name="left_shoulder">
    <origin xyz="0.15 0.1 0.6" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.08"/>
    </geometry>
  </collision>

  <collision name="right_shoulder">
    <origin xyz="0.15 -0.1 0.6" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.08"/>
    </geometry>
  </collision>
</link>
```

## Environmental Physics

### Ground Plane and Surfaces

Different surfaces affect humanoid robot behavior:

```xml
<!-- Standard ground plane -->
<model name="ground_plane">
  <static>true</static>
  <link name="link">
    <collision name="collision">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.8</mu>  <!-- High friction for walking -->
            <mu2>0.8</mu2>
          </ode>
        </friction>
        <bounce>
          <restitution_coefficient>0.01</restitution_coefficient>
        </bounce>
      </surface>
    </collision>
    <visual name="visual">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
      <material>
        <ambient>0.7 0.7 0.7 1</ambient>
        <diffuse>0.7 0.7 0.7 1</diffuse>
      </material>
    </visual>
  </link>
</model>

<!-- Slippery surface -->
<model name="slippery_floor">
  <static>true</static>
  <link name="link">
    <collision name="collision">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>10 10</size>
        </plane>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.1</mu>  <!-- Low friction for testing balance -->
            <mu2>0.1</mu2>
          </ode>
        </friction>
      </surface>
    </collision>
  </link>
</model>
```

### Furniture and Obstacles

For VLA system testing, include realistic environmental objects:

```xml
<!-- Kitchen table -->
<model name="kitchen_table">
  <pose>2 0 0 0 0 0</pose>
  <link name="table_top">
    <collision>
      <geometry>
        <box size="1.5 0.8 0.02"/>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.5</mu>
            <mu2>0.5</mu2>
          </ode>
        </friction>
      </surface>
    </collision>
    <visual>
      <geometry>
        <box size="1.5 0.8 0.02"/>
      </geometry>
      <material>
        <ambient>0.6 0.4 0.2 1</ambient>
        <diffuse>0.6 0.4 0.2 1</diffuse>
      </material>
    </visual>
  </link>

  <link name="leg1">
    <pose>0.65 0.35 -0.4 0 0 0</pose>
    <collision>
      <geometry>
        <cylinder length="0.8" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Additional legs -->
  <joint name="leg1_joint" type="fixed">
    <parent>table_top</parent>
    <child>leg1</child>
  </joint>
</model>

<!-- Objects for manipulation -->
<model name="red_cup">
  <pose>2.1 0.1 0.81 0 0 0</pose>
  <link name="cup_body">
    <inertial>
      <mass>0.2</mass>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
    <collision>
      <geometry>
        <cylinder length="0.1" radius="0.04"/>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.6</mu>
            <mu2>0.6</mu2>
          </ode>
        </friction>
      </surface>
    </collision>
    <visual>
      <geometry>
        <cylinder length="0.1" radius="0.04"/>
      </geometry>
      <material>
        <ambient>1 0 0 1</ambient>
        <diffuse>1 0 0 1</diffuse>
      </material>
    </visual>
  </link>
</model>
```

## Contact Sensors and Force Feedback

### Force/Torque Sensors in Joints

For realistic humanoid control, add force feedback:

```xml
<gazebo>
  <plugin name="ft_sensor_left_foot" filename="libgazebo_ros_ft_sensor.so">
    <update_rate>100</update_rate>
    <always_on>true</always_on>
    <body_name>left_foot</body_name>
    <frame_name>left_foot</frame_name>
    <topic>left_foot/force_torque</topic>
  </plugin>
</gazebo>

<gazebo>
  <plugin name="ft_sensor_right_foot" filename="libgazebo_ros_ft_sensor.so">
    <update_rate>100</update_rate>
    <always_on>true</always_on>
    <body_name>right_foot</body_name>
    <frame_name>right_foot</frame_name>
    <topic>right_foot/force_torque</topic>
  </plugin>
</gazebo>
```

## Wind and External Forces

### Environmental Disturbances

For testing VLA system robustness:

```xml
<!-- Wind force on humanoid -->
<world name="windy_environment">
  <gravity>0 0 -9.8</gravity>

  <!-- Add wind plugin -->
  <gazebo>
    <plugin name="wind_plugin" filename="libgazebo_ros_wind.so">
      <update_rate>10</update_rate>
      <wind_direction>1 0 0</wind_direction>
      <wind_force>0.5 0 0</wind_force>
      <linear_wind_gust_min_period>10</linear_wind_gust_min_period>
      <linear_wind_gust_max_period>100</linear_wind_gust_max_period>
      <linear_wind_gust_min_amplitude>0</linear_wind_gust_min_amplitude>
      <linear_wind_gust_max_amplitude>0.5</linear_wind_gust_max_amplitude>
    </plugin>
  </gazebo>

  <physics type="ode">
    <max_step_size>0.001</max_step_size>
    <real_time_factor>1.0</real_time_factor>
  </physics>
</world>
```

## Simulation Validation

### Physics Validation Techniques

1. **Static Balance**: Verify the robot remains stable when standing
2. **Dynamic Response**: Test realistic acceleration and deceleration
3. **Contact Behavior**: Validate collision responses and friction
4. **Energy Conservation**: Check for realistic energy dissipation
5. **Stability Margins**: Test response to external disturbances

### Validation Metrics

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped
import numpy as np

class PhysicsValidator(Node):
    def __init__(self):
        super().__init__('physics_validator')

        # Subscribe to joint states and robot pose
        self.joint_sub = self.create_subscription(
            JointState, 'joint_states', self.joint_callback, 10
        )

        # Track robot COM and stability
        self.com_history = []
        self.stability_threshold = 0.1  # meters

    def joint_callback(self, msg):
        # Calculate center of mass position
        com_pos = self.calculate_com_position(msg)

        # Check stability based on support polygon
        support_polygon = self.calculate_support_polygon()
        stability_margin = self.calculate_stability_margin(com_pos, support_polygon)

        if stability_margin < self.stability_threshold:
            self.get_logger().warn(f'Robot unstable: margin = {stability_margin:.3f}m')

        self.com_history.append(com_pos)

    def calculate_com_position(self, joint_state):
        # Calculate center of mass based on joint positions and link masses
        # Implementation depends on robot URDF
        pass

    def calculate_support_polygon(self):
        # Calculate support polygon based on contact points
        # For biped: convex hull of feet contact points
        pass

    def calculate_stability_margin(self, com_pos, support_polygon):
        # Calculate minimum distance from COM to support polygon edge
        pass
```

## Performance Optimization

### Physics Performance Settings

```xml
<physics type="ode">
  <!-- Performance-optimized settings -->
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>

  <ode>
    <solver>
      <type>quick</type>    <!-- Fast solver -->
      <iters>20</iters>     <!-- Balance accuracy and speed -->
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0.001</cfm>      <!-- Constraint mixing -->
      <erp>0.2</erp>        <!-- Error reduction -->
    </constraints>
  </ode>
</physics>
```

## Integration with VLA Systems

Realistic physics enables:
- **Safe Command Testing**: Validate voice commands in physics-accurate environments
- **Balance Validation**: Test responses to external disturbances
- **Manipulation Planning**: Verify grasp and manipulation in physics simulation
- **Navigation Safety**: Test path planning with realistic collision detection
- **Performance Analysis**: Evaluate system performance under various conditions

## Best Practices

1. **Conservative Collision Models**: Make collision geometry slightly larger than visual
2. **Realistic Friction**: Use appropriate friction coefficients for surfaces
3. **Stable Time Steps**: Use small enough time steps for humanoid stability
4. **Validate Against Reality**: Compare simulation to physical robot when possible
5. **Test Edge Cases**: Verify behavior under extreme conditions
6. **Optimize Performance**: Balance accuracy with real-time simulation requirements

These physics configurations ensure that VLA systems developed in simulation will behave predictably when deployed to physical humanoid robots.