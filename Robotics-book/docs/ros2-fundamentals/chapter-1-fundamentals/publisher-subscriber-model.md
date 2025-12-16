---
sidebar_position: 3
---

# Publisher-Subscriber Model

## Asynchronous Communication in ROS 2

The publisher-subscriber model is the cornerstone of ROS 2's communication architecture. It enables decoupled, asynchronous communication between nodes, which is essential for the real-time requirements of humanoid robot systems.

## Core Concept

In the publisher-subscriber model:
- **Publishers** send messages to named topics without knowing who will receive them
- **Subscribers** receive messages from named topics without knowing who sent them
- **ROS 2 Middleware** handles the routing between publishers and subscribers

This creates a loose coupling that allows for:
- Independent development of components
- Easy replacement of implementations
- Scalable system architecture

## Architecture Pattern

```
[Publisher Node 1] ──┐
                     ├─── [Topic: /sensor_data] ──┬── [Subscriber Node 1]
[Publisher Node 2] ──┤                           │
                     │                           ├── [Subscriber Node 2]
[Publisher Node 3] ──┘                           │
                                                 └── [Subscriber Node 3]
```

## Implementation Example

### Publisher Implementation

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

class JointStatePublisher(Node):
    def __init__(self):
        super().__init__('joint_state_publisher')

        # Create publisher for joint states
        self.publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10  # QoS history depth
        )

        # Create timer to publish at 50 Hz
        self.timer = self.create_timer(0.02, self.publish_joint_states)

        # Simulated joint positions
        self.joint_positions = [0.0, 0.1, 0.2, 0.3]  # Example joint angles

    def publish_joint_states(self):
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        msg.name = ['joint1', 'joint2', 'joint3', 'joint4']
        msg.position = self.joint_positions
        msg.velocity = [0.0, 0.0, 0.0, 0.0]
        msg.effort = [0.0, 0.0, 0.0, 0.0]

        self.publisher.publish(msg)
        self.joint_positions = [pos + 0.01 for pos in self.joint_positions]  # Simulate movement
```

### Subscriber Implementation

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateSubscriber(Node):
    def __init__(self):
        super().__init__('joint_state_subscriber')

        # Create subscription to joint states
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10  # QoS history depth
        )

        self.subscription  # prevent unused variable warning

    def joint_state_callback(self, msg):
        self.get_logger().info(
            f'Received joint states: '
            f'Positions: {msg.position}, '
            f'Velocities: {msg.velocity}'
        )

        # Process joint states for control or monitoring
        self.process_joint_data(msg)

    def process_joint_data(self, joint_state_msg):
        # Implement your joint processing logic here
        # For example: check for joint limits, calculate inverse kinematics, etc.
        pass
```

## Quality of Service Considerations

Different types of data require different QoS profiles:

### Sensor Data (e.g., cameras, lidars)
```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

sensor_qos = QoSProfile(
    depth=5,  # Only keep last 5 messages
    reliability=ReliabilityPolicy.BEST_EFFORT,  # Don't require every message
    history=HistoryPolicy.KEEP_LAST  # Keep only recent messages
)
```

### Critical Control Data
```python
control_qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,  # Ensure delivery
    history=HistoryPolicy.KEEP_ALL  # Keep all messages
)
```

## Benefits for Humanoid Robotics

The publisher-subscriber model provides several advantages for humanoid robots:

### 1. Real-time Performance
- Asynchronous communication prevents blocking
- Multiple sensors can publish simultaneously
- Control loops can run independently

### 2. Modularity
- Perception nodes can be swapped without affecting control
- Different control algorithms can be tested easily
- Sensor fusion becomes straightforward

### 3. Fault Tolerance
- If one subscriber fails, others continue operating
- Publishers don't need to know about subscriber failures
- System can degrade gracefully

## Advanced Patterns

### Multiple Publishers, Single Subscriber
```python
# Multiple sensor nodes can publish to the same topic
# Navigation node subscribes to all sensor data
```

### Single Publisher, Multiple Subscribers
```python
# Robot state publisher sends to multiple consumers:
# - Visualization tools
# - Control algorithms
# - Logging systems
# - Safety monitors
```

## Connection Events

You can monitor connections between publishers and subscribers:

```python
def publisher_callback(self):
    # Called when a subscriber connects/disconnects
    count = self.publisher.get_subscription_count()
    self.get_logger().info(f'Number of subscribers: {count}')
```

## Best Practices for Humanoid Robots

1. **Use appropriate QoS settings** for your data type
2. **Implement proper message throttling** to avoid overwhelming subscribers
3. **Use meaningful topic names** that reflect the data content
4. **Consider bandwidth limitations** in wireless scenarios
5. **Implement message validation** to handle corrupted data
6. **Monitor connection status** for critical systems

## Integration with Vision-Language-Action Systems

In VLA systems, the publisher-subscriber model enables:
- Voice input nodes publishing commands to AI planning nodes
- LLM nodes publishing action sequences to execution nodes
- Sensor nodes providing perception data for action validation
- Status nodes providing feedback to users

This architecture allows for the seamless flow of information from voice commands to physical actions while maintaining system modularity and reliability.