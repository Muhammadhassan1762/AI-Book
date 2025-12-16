# Digital Twin System Diagrams

This document describes the key diagrams that should be created for the Digital Twin (Gazebo & Unity) module.

## Architecture Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Unity         │    │   ROS Bridge     │    │   Gazebo        │
│   Visual        │◄──►│   (Synchronization) │◄──►│   Physics       │
│   Simulation    │    │   Layer)         │    │   Simulation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Human-Robot   │    │   Sensor Data    │    │   Robot State   │
│   Interaction   │    │   Processing     │    │   Management    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

The architecture diagram shows how Unity and Gazebo are connected through the ROS bridge layer, with each system handling its specialized function.

## Sensor Simulation Diagram

```
                    ┌─────────────────┐
                    │   Robot Model   │
                    │   (URDF/SDF)    │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   LiDAR       │   │  Depth Camera │   │     IMU       │
│ Simulation    │   │ Simulation    │   │ Simulation    │
│  - Range data │   │  - RGB image  │   │  - Orientation│
│  - Noise      │   │  - Depth map  │   │  - Acceleration│
│  - FOV        │   │  - Noise      │   │  - Angular Vel│
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│                   ROS Topics                            │
│  /laser_scan     /depth_camera/image_raw    /imu/data  │
└─────────────────────────────────────────────────────────┘
```

This diagram illustrates how different sensors are simulated on the robot model and publish data to ROS topics.

## Digital Twin Synchronization Flow

```
Time:  t0 ────── t1 ────── t2 ────── t3 ────── t4

Gazebo:  [Physics]──►[Physics]──►[Physics]──►[Physics]
          State      State      State      State

Unity:   [Visual] ──►[Visual] ──►[Visual] ──►[Visual]
          Render     Render     Render     Render

Sync:    [Sync] ────►[Sync] ────►[Sync] ────►[Sync]
         Event       Event       Event       Event
```

This sequence diagram shows how physics simulation, visual rendering, and synchronization events occur over time.

## Physics vs Visual Layer Separation

```
┌─────────────────────────────────────────────────────────┐
│                    Unity Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  High-Fidelity│  │  Human-    │  │  Immersive  │    │
│  │  Rendering   │  │  Interaction│  │  Interface  │    │
│  │  (Visual)    │  │             │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                           │
                    ┌─────────────┐
                    │  ROS Bridge │
                    │  (Data Sync)│
                    └─────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                   Gazebo Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Accurate   │  │  Collision  │  │  Sensor     │    │
│  │  Physics    │  │  Detection  │  │  Simulation │    │
│  │  Simulation │  │             │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

This diagram illustrates the clear separation between visual and physics layers in the digital twin system.