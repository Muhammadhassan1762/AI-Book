---
sidebar_position: 3
---

# Publisher-Subscriber Model

## Understanding the Core Communication Pattern

The publisher-subscriber model is the most fundamental communication pattern in ROS 2. It enables decoupled communication between nodes, allowing for flexible and scalable robot systems. Understanding this model is essential for creating effective robot control systems.

## How the Publisher-Subscriber Model Works

### Basic Concept

In the publisher-subscriber model:

1. **Publishers** create and send messages to named topics
2. **Subscribers** receive messages from named topics they are interested in
3. The ROS 2 middleware handles routing messages from publishers to subscribers
4. Publishers and subscribers don't need to know about each other directly

### The Communication Flow

```
[Publisher Node] ----(Message)----> [Topic: chatter] ----(Message)----> [Subscriber Node]
     |                                    |                                     |
Create Message                    ROS 2 Middleware                   Process Message
```

### Key Principles

- **Decoupling**: Publishers don't know who (if anyone) is subscribed to their topics
- **Flexibility**: You can add or remove subscribers without changing the publisher
- **Scalability**: Multiple subscribers can receive the same data stream
- **Asynchronous**: Publishers and subscribers operate independently

## The Publisher-Subscriber in Robot Control

### Sensor Data Flow

In robot control systems, the publisher-subscriber model is often used for:

- **Sensor Data Distribution**: Sensors publish data that multiple controllers can use
- **Command Distribution**: Controllers publish commands that actuators can execute
- **Status Updates**: Components publish status information for monitoring

### Example Robot Control Architecture

```
[IMU Sensor] ----> [sensor_data] ----> [State Estimator]
[Lidar] ----> [scan_data] ----> [Obstacle Detector] ----> [Path Planner]
[Path Planner] ----> [cmd_vel] ----> [Motor Controller] ----> [Wheels]
```

## Practical Example: Our Basic Publisher-Subscriber

Let's examine our example more closely:

### Publisher Code Analysis

```python
class BasicPublisher(Node):
    def __init__(self):
        super().__init__('basic_publisher')
        # Create publisher for 'chatter' topic with String messages
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        # Create timer to send messages at regular intervals
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)  # Publish the message
        self.i += 1
```

### Subscriber Code Analysis

```python
class BasicSubscriber(Node):
    def __init__(self):
        super().__init__('basic_subscriber')
        # Create subscription to 'chatter' topic
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,  # Callback function
            10)  # Queue size

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')
```

## Advanced Publisher-Subscriber Concepts

### Quality of Service (QoS) Settings

ROS 2 provides Quality of Service settings to control how messages are delivered:

- **Reliability**: Reliable (all messages delivered) or Best Effort (try to deliver)
- **Durability**: Keep last message for late-joining subscribers
- **History**: How many messages to keep in the queue

### Publisher Options

```python
# Create publisher with custom QoS
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

qos_profile = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST
)

self.publisher_ = self.create_publisher(String, 'chatter', qos_profile)
```

## Best Practices for Publisher-Subscriber Design

### 1. Topic Naming Conventions

- Use descriptive names that clearly indicate the data type
- Follow a consistent naming scheme throughout your robot
- Group related topics with common prefixes

### 2. Message Design

- Keep messages simple and focused on a single concept
- Use appropriate data types for your application
- Consider the frequency and size of messages for performance

### 3. Publisher Design

- Publish at an appropriate rate for your application
- Handle errors gracefully if publishing fails
- Consider using latching for static data

### 4. Subscriber Design

- Process messages efficiently to avoid queue overflow
- Use appropriate queue sizes for your application
- Consider threading if message processing is time-consuming

## Common Publisher-Subscriber Patterns

### Sensor Fusion Pattern

Multiple sensor nodes publish to different topics, and a fusion node subscribes to all of them:

```
[IMU] ----> [imu_data]
                    \
                     ----> [SensorFusion] ----> [fused_data]
                    /
[Lidar] ----> [lidar_data]
```

### Control Loop Pattern

Controller publishes commands, and a monitoring node subscribes to both commands and feedback:

```
[Controller] ----> [cmd_vel] ----> [Robot]
                    |
                    v
               [Command Monitor]
```

## Troubleshooting Publisher-Subscriber Issues

### Common Problems

1. **No messages received**: Check topic names match exactly
2. **Messages delayed**: Check QoS settings compatibility
3. **Queue overflow**: Increase queue size or process messages faster
4. **Node not visible**: Ensure nodes are on the same ROS domain

### Debugging Tools

- `ros2 topic list`: See all available topics
- `ros2 topic echo <topic_name>`: Monitor messages on a topic
- `ros2 node list`: See all active nodes
- `ros2 run rqt_graph rqt_graph`: Visualize the ROS graph

## The Role in Robot Control Systems

The publisher-subscriber model enables distributed robot control by:

- Allowing different control components to operate independently
- Providing a standardized way to share sensor data and commands
- Enabling fault tolerance through decoupled communication
- Supporting real-time performance with efficient message passing

## Summary

The publisher-subscriber model is the backbone of ROS 2 communication. By understanding and properly implementing this pattern, you can create robust, scalable robot control systems. Remember to design your topics thoughtfully, consider the timing and frequency of your messages, and use appropriate QoS settings for your application's requirements.

## Next Steps

- **Continue to Chapter 2**: Learn how to connect [AI decision-making systems](../chapter-2-ai-agents/index.md) with robot controllers using the communication patterns you learned here.
- **Explore URDF modeling**: Once you're comfortable with communication patterns, learn to create robot models in [Chapter 3: Humanoid Modeling with URDF](../chapter-3-urdf-modeling/index.md).

In the next chapter, we'll explore how to connect AI decision-making to robot controllers using this communication model.