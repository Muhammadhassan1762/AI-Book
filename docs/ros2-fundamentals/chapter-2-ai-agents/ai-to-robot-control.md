---
sidebar_position: 3
---

# AI-to-Robot Control

## Creating Intelligent Robot Control Systems

In this section, we'll explore how to design complete systems that connect AI decision-making to robot control. This involves creating architectures that handle perception, reasoning, and action in a coordinated way, forming the foundation of autonomous robotic systems.

## The Perception-Reasoning-Action Loop

The fundamental pattern for AI-robot control follows the perception-reasoning-action cycle:

```
[Perception] --> [Reasoning/AI] --> [Action] --> [Environment] --> [Perception]
     ^                                                      |
     |                                                      |
     +------------------------------------------------------+
```

### 1. Perception Layer
The perception layer processes sensor data to understand the environment:

- **Sensor Fusion**: Combining data from multiple sensors (cameras, lidars, IMUs)
- **Feature Extraction**: Identifying relevant information from raw sensor data
- **State Estimation**: Determining the robot's state and the environment state

### 2. Reasoning/AI Layer
The reasoning layer makes decisions based on the perceived information:

- **Planning**: Determining sequences of actions to achieve goals
- **Learning**: Adapting behavior based on experience
- **Decision Making**: Choosing appropriate actions based on current state

### 3. Action Layer
The action layer executes the decisions made by the reasoning layer:

- **Control**: Converting high-level commands to low-level actuator commands
- **Execution**: Carrying out the planned actions
- **Monitoring**: Tracking the execution and detecting failures

## Designing the Control Architecture

### Hierarchical Control Structure

A typical AI-robot control system uses a hierarchical structure:

```
High-Level AI (Goals, Tasks)
         |
Mid-Level Planner (Paths, Behaviors)
         |
Low-Level Controller (Motor Commands)
```

Each level operates at different time scales and abstraction levels:

- **High-Level**: Long-term goals, infrequent updates (seconds to minutes)
- **Mid-Level**: Path planning, moderate frequency (1-10 Hz)
- **Low-Level**: Control loops, high frequency (50-1000 Hz)

### Example Architecture

Let's look at a complete example architecture for an autonomous navigation system:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String
import numpy as np


class AINavSystem(Node):
    """
    Complete AI-robot navigation system with perception, reasoning, and action layers.
    """

    def __init__(self):
        super().__init__('ai_nav_system')

        # Perception layer - sensor subscriptions
        self.lidar_subscription = self.create_subscription(
            LaserScan, 'scan', self.lidar_callback, 10)
        self.camera_subscription = self.create_subscription(
            Image, 'camera/image_raw', self.camera_callback, 10)

        # Reasoning layer - goal and plan management
        self.goal_subscription = self.create_subscription(
            PoseStamped, 'goal_pose', self.goal_callback, 10)

        # Action layer - command publishing
        self.cmd_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # State management
        self.current_goal = None
        self.current_plan = []
        self.robot_pose = None

        # Processing timers for each layer
        self.perception_timer = self.create_timer(0.1, self.perception_step)
        self.reasoning_timer = self.create_timer(0.5, self.reasoning_step)
        self.action_timer = self.create_timer(0.02, self.action_step)  # 50 Hz

        self.get_logger().info('AI Navigation System initialized')

    def lidar_callback(self, msg):
        """Process LIDAR data for obstacle detection"""
        # Store for perception layer processing
        self.lidar_data = msg

    def camera_callback(self, msg):
        """Process camera data for visual perception"""
        # Store for perception layer processing
        self.camera_data = msg

    def goal_callback(self, msg):
        """Receive navigation goal"""
        self.current_goal = msg.pose
        self.get_logger().info(f'New goal received: {msg.pose}')

    def perception_step(self):
        """Process sensor data to update environment model"""
        if hasattr(self, 'lidar_data'):
            # Process LIDAR data to detect obstacles
            obstacles = self.process_lidar_for_obstacles(self.lidar_data)
            self.update_obstacle_map(obstacles)

        if hasattr(self, 'camera_data'):
            # Process camera data for visual features
            features = self.process_camera_for_features(self.camera_data)
            self.update_feature_map(features)

    def reasoning_step(self):
        """Make high-level decisions based on perception"""
        if self.current_goal and self.robot_pose:
            # Plan path to goal considering obstacles
            new_plan = self.plan_path_to_goal(
                self.robot_pose,
                self.current_goal,
                self.get_current_obstacle_map()
            )
            if new_plan:
                self.current_plan = new_plan

    def action_step(self):
        """Execute low-level commands"""
        if self.current_plan:
            # Generate velocity command based on current plan
            cmd = self.generate_velocity_command(
                self.robot_pose,
                self.current_plan,
                self.get_current_obstacle_map()
            )
            self.cmd_publisher.publish(cmd)

    def process_lidar_for_obstacles(self, scan_msg):
        """Extract obstacle information from LIDAR scan"""
        # Convert to numpy array
        ranges = np.array(scan_msg.ranges)
        angles = np.linspace(
            scan_msg.angle_min,
            scan_msg.angle_max,
            len(scan_msg.ranges)
        )

        # Filter out invalid readings
        valid_mask = np.isfinite(ranges)
        valid_ranges = ranges[valid_mask]
        valid_angles = angles[valid_mask]

        # Calculate obstacle positions in robot frame
        x_points = valid_ranges * np.cos(valid_angles)
        y_points = valid_ranges * np.sin(valid_angles)

        # Group nearby points into obstacles
        obstacles = self.cluster_obstacle_points(x_points, y_points)
        return obstacles

    def plan_path_to_goal(self, start_pose, goal_pose, obstacles):
        """Plan a path from start to goal avoiding obstacles"""
        # This would typically use a path planning algorithm like A* or RRT
        # For this example, we'll return a simple direct path
        path = [start_pose, goal_pose]  # Simplified
        return path

    def generate_velocity_command(self, robot_pose, plan, obstacles):
        """Generate velocity command to follow the plan"""
        cmd = Twist()

        if plan and len(plan) > 1:
            # Calculate direction to next waypoint
            target_x = plan[1].position.x  # Simplified access
            target_y = plan[1].position.y

            # Calculate distance and angle to target
            dx = target_x - robot_pose.position.x
            dy = target_y - robot_pose.position.y
            distance = np.sqrt(dx*dx + dy*dy)

            # Simple proportional controller
            cmd.linear.x = min(distance * 0.5, 0.5)  # Max 0.5 m/s
            cmd.angular.z = np.arctan2(dy, dx) * 1.0  # Heading control

        return cmd


def main(args=None):
    rclpy.init(args=args)
    ai_nav_system = AINavSystem()

    try:
        rclpy.spin(ai_nav_system)
    except KeyboardInterrupt:
        pass
    finally:
        ai_nav_system.destroy_node()
        rclpy.shutdown()
```

## AI Integration Patterns

### 1. Behavior Trees
Behavior trees provide a structured way to organize AI behaviors:

```python
class BehaviorTreeAI(Node):
    def __init__(self):
        super().__init__('behavior_tree_ai')
        # Define behaviors as methods
        self.behaviors = {
            'find_path': self.find_path_behavior,
            'follow_path': self.follow_path_behavior,
            'avoid_obstacles': self.avoid_obstacles_behavior,
            'reached_goal': self.reached_goal_behavior
        }

    def execute_behavior_tree(self):
        """Execute the behavior tree based on current state"""
        if self.check_goal_reached():
            return self.behaviors['reached_goal']()
        elif self.check_obstacles():
            return self.behaviors['avoid_obstacles']()
        elif not self.current_plan:
            return self.behaviors['find_path']()
        else:
            return self.behaviors['follow_path']()
```

### 2. Finite State Machines
FSMs are useful for systems with discrete operational modes:

```python
from enum import Enum

class RobotState(Enum):
    IDLE = 1
    NAVIGATING = 2
    AVOIDING_OBSTACLES = 3
    REACHED_GOAL = 4

class StateMachineAI(Node):
    def __init__(self):
        super().__init__('state_machine_ai')
        self.current_state = RobotState.IDLE

    def state_machine_step(self):
        """Execute the current state's behavior"""
        if self.current_state == RobotState.IDLE:
            self.idle_behavior()
        elif self.current_state == RobotState.NAVIGATING:
            self.navigating_behavior()
        elif self.current_state == RobotState.AVOIDING_OBSTACLES:
            self.avoiding_obstacles_behavior()
        elif self.current_state == RobotState.REACHED_GOAL:
            self.reached_goal_behavior()
```

### 3. Reinforcement Learning Integration
For adaptive systems, you can integrate reinforcement learning:

```python
class RLLearningAI(Node):
    def __init__(self):
        super().__init__('rl_learning_ai')
        # Initialize RL model
        self.rl_model = self.initialize_rl_model()
        self.episode_step = 0

    def perception_callback(self, sensor_data):
        """Process sensor data and get RL action"""
        state = self.convert_sensor_to_state(sensor_data)
        action = self.rl_model.predict(state)
        self.execute_rl_action(action)

        # Store experience for learning
        self.store_experience(state, action, sensor_data)

    def store_experience(self, state, action, next_sensor_data):
        """Store experience for future learning"""
        # This would typically store (state, action, reward, next_state) tuples
        pass
```

## Safety and Robustness Considerations

### 1. Fallback Behaviors
Always implement safe fallback behaviors:

```python
def safe_fallback_behavior(self):
    """Emergency stop and safe state"""
    cmd = Twist()
    cmd.linear.x = 0.0
    cmd.angular.z = 0.0
    self.cmd_publisher.publish(cmd)
    self.get_logger().warn('Executing safe fallback behavior')
```

### 2. Watchdog Timers
Monitor system health and respond to failures:

```python
def __init__(self):
    super().__init__('ai_control_system')
    # Watchdog timer for system health
    self.watchdog_timer = self.create_timer(1.0, self.watchdog_callback)
    self.last_sensor_time = self.get_clock().now()

def sensor_callback(self, msg):
    """Update sensor time for watchdog"""
    self.last_sensor_time = self.get_clock().now()

def watchdog_callback(self):
    """Check system health"""
    current_time = self.get_clock().now()
    time_since_sensor = (current_time - self.last_sensor_time).nanoseconds / 1e9

    if time_since_sensor > 5.0:  # No sensor data for 5 seconds
        self.get_logger().error('Sensor timeout - executing safe behavior')
        self.safe_fallback_behavior()
```

### 3. Graceful Degradation
Design systems that can operate with reduced capabilities:

```python
def check_sensor_health(self):
    """Check which sensors are operational"""
    sensors_available = {}

    # Check LIDAR
    if hasattr(self, 'lidar_data'):
        sensors_available['lidar'] = True
    else:
        sensors_available['lidar'] = False

    # Check camera
    if hasattr(self, 'camera_data'):
        sensors_available['camera'] = True
    else:
        sensors_available['camera'] = False

    return sensors_available

def adaptive_control(self, sensors_available):
    """Adjust control strategy based on available sensors"""
    if sensors_available['lidar'] and sensors_available['camera']:
        # Full perception capability
        return self.full_perception_control()
    elif sensors_available['lidar']:
        # LIDAR-only navigation
        return self.lidar_only_control()
    else:
        # Minimal safe behavior
        return self.emergency_safe_behavior()
```

## Performance Optimization

### 1. Threading for AI Processing
Use threading for computationally expensive AI operations:

```python
import threading
from concurrent.futures import ThreadPoolExecutor

class ThreadedAI(Node):
    def __init__(self):
        super().__init__('threaded_ai')
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.ai_result = None

    def sensor_callback(self, msg):
        """Submit AI processing to thread pool"""
        future = self.executor.submit(self.ai_processing_function, msg)
        future.add_done_callback(self.ai_result_callback)

    def ai_result_callback(self, future):
        """Handle AI result when processing is complete"""
        try:
            result = future.result()
            self.ai_result = result
            # Publish command based on result
        except Exception as e:
            self.get_logger().error(f'AI processing failed: {e}')
```

### 2. Model Optimization
Optimize AI models for real-time performance:

```python
def optimize_model_for_inference(self, model):
    """Optimize model for faster inference"""
    # Example: Convert to TensorRT (NVIDIA) or OpenVINO
    # This would depend on your specific model and hardware
    pass
```

## Testing AI-Robot Systems

### 1. Unit Testing for AI Logic
Test AI components independently:

```python
import unittest
import numpy as np

class TestAINavigation(unittest.TestCase):
    def test_obstacle_detection(self):
        """Test obstacle detection algorithm"""
        ai_node = AINavSystem()

        # Create test LIDAR data with known obstacles
        test_scan = self.create_test_lidar_data()

        obstacles = ai_node.process_lidar_for_obstacles(test_scan)

        # Verify obstacles are detected at expected locations
        self.assertGreater(len(obstacles), 0)
```

### 2. Integration Testing
Test the complete AI-robot system:

```python
def test_ai_robot_integration(self):
    """Test complete AI-robot system"""
    # Use ROS 2 testing framework
    # Launch simulation environment
    # Send known sensor data
    # Verify appropriate commands are generated
    pass
```

## Summary

Creating effective AI-robot control systems requires careful consideration of the complete perception-reasoning-action loop. By following the architectural patterns and best practices outlined in this section, you can build robust, safe, and efficient systems that effectively bridge AI decision-making with physical robot control.

The key to success is balancing the complexity of AI algorithms with the real-time requirements of robot control, while maintaining safety and reliability. Always design with fallback behaviors and graceful degradation in mind.

## Next Steps

- **Continue to Chapter 3**: Learn how to create [robot models using URDF](../chapter-3-urdf-modeling/index.md) and integrate them with the AI-robot control systems you've learned about.
- **Review fundamentals**: If you need to refresh your knowledge of [ROS 2 fundamentals](../chapter-1-fundamentals/index.md), refer back to Chapter 1.

In the next chapter, we'll explore how to model robots using URDF and integrate these models with our AI-robot control systems.