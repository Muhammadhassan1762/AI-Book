---
title: Gravity, Collisions, and Environments
sidebar_position: 2
---

# Gravity, Collisions, and Environments

This section covers the fundamentals of physics simulation in Gazebo, focusing on how to configure gravity, collisions, and environments for humanoid robots.

## Gravity Configuration

Gravity is a fundamental aspect of physics simulation that affects how objects move and interact in the virtual world. In Gazebo, gravity is typically set to match Earth's gravity (9.81 m/s²) in the negative Z direction.

### Setting Gravity in Gazebo

Gravity can be configured in Gazebo world files using the `<gravity>` tag:

```xml
<sdf version="1.7">
  <world name="basic_world">
    <!-- Set gravity to Earth's gravity: 0, 0, -9.81 -->
    <gravity>0 0 -9.81</gravity>
    <!-- World content goes here -->
  </world>
</sdf>
```

## Collision Detection

Collision detection is crucial for realistic robot simulation. It determines how robots interact with the environment and with themselves (self-collision).

### Collision Properties

Each link in a robot model should have collision properties defined:

```xml
<link name="link_name">
  <collision name="collision">
    <geometry>
      <box>
        <size>0.1 0.1 0.1</size>
      </box>
    </geometry>
  </collision>
</link>
```

## Environment Setup

The environment in which your humanoid robot operates significantly affects its behavior and the realism of the simulation.

### Creating Basic Environments

Environments can be created using Gazebo's world files, which define:
- Terrain and ground planes
- Objects and obstacles
- Lighting conditions
- Physics properties

## Simulation Realism Considerations

To ensure your physics simulation accurately represents real-world behavior:

1. **Mass Properties**: Ensure robot links have realistic mass and inertia values
2. **Friction**: Set appropriate friction coefficients for different materials
3. **Damping**: Apply realistic damping values to simulate energy loss
4. **Contact Properties**: Configure contact parameters for accurate collision response