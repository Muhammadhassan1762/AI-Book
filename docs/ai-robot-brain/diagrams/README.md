# AI-Robot Brain Diagrams

This directory contains descriptions of diagrams for the AI-Robot Brain module. These diagrams illustrate key concepts and workflows.

## Diagram: Perception-Mapping-Action Pipeline

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Isaac Sim     │───▶│  Isaac ROS       │───▶│    Nav2         │
│  (Synthetic      │    │  (VSLAM &       │    │  (Navigation)   │
│   Data Gen)      │    │   Perception)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RGB/Depth/    │    │  Map & Pose      │    │  Path &         │
│   Segmentation  │    │  Estimation      │    │  Execution      │
│   Datasets      │    │                 │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Diagram: VSLAM Process Flow

```
Camera Input → Feature Detection → Pose Estimation → Map Building → Trajectory Tracking
```

## Diagram: Navigation Workflow

```
Map Input → Path Planning → Local Planning → Obstacle Avoidance → Robot Control
```

## Diagram: System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI-Robot Brain System                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Perception │  │   Mapping   │  │ Navigation  │              │
│  │             │  │             │  │             │              │
│  │ • RGB       │  │ • Feature   │  │ • Global    │              │
│  │ • Depth     │  │   Matching  │  │   Planner   │              │
│  │ • Seg       │  │ • Pose      │  │ • Local     │              │
│  │             │  │   Est       │  │   Planner   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Diagram: Data Flow

```
Synthetic Data Generation → Training Data → Perception Models → Real-time Processing → Navigation Decisions
```