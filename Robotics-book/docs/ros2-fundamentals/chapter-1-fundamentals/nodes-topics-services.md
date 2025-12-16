---
sidebar_position: 2
---

# Nodes, Topics, and Services

## Understanding ROS 2 Communication

In ROS 2, communication between different parts of a robotic system happens through three primary mechanisms: nodes, topics, and services. Understanding these concepts is fundamental to developing humanoid robots.

## Nodes: The Building Blocks

A **node** is a single executable that uses ROS 2 to communicate with other nodes. In humanoid robot systems, nodes typically handle specific functions:

- **Sensor Nodes**: Process data from cameras, IMUs, joint encoders
- **Control Nodes**: Send commands to actuators and motors
- **Perception Nodes**: Process sensor data to detect objects, people, or navigate
- **Planning Nodes**: Generate trajectories and action plans
- **AI Nodes**: Process high-level commands and make decisions

### Node Example in Python

```python
import rclpy
from rclpy.node import Node

class RobotControllerNode(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.get_logger().info('Robot Controller node started')

def main(args=None):
    rclpy.init(args=args)
    node = RobotControllerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Topics: Asynchronous Communication

**Topics** enable asynchronous communication using a publish-subscribe model. This is ideal for continuous data streams like sensor readings or robot state information.

### Publisher Example

```python
from std_msgs.msg import String
import rclpy
from rclpy.node import Node

class VoiceCommandPublisher(Node):
    def __init__(self):
        super().__init__('voice_command_publisher')
        self.publisher = self.create_publisher(String, 'voice_commands', 10)
        self.timer = self.create_timer(0.5, self.publish_command)

    def publish_command(self):
        msg = String()
        msg.data = 'Move to kitchen'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
```

### Subscriber Example

```python
from std_msgs.msg import String
import rclpy
from rclpy.node import Node

class CommandSubscriber(Node):
    def __init__(self):
        super().__init__('command_subscriber')
        self.subscription = self.create_subscription(
            String,
            'voice_commands',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'Received command: {msg.data}')
```

## Services: Synchronous Communication

**Services** provide synchronous request-response communication. This is useful when you need to wait for a specific result, like asking for a plan or requesting sensor data.

### Service Server Example

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class AddService(Node):
    def __init__(self):
        super().__init__('add_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_callback)

    def add_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {response.sum}')
        return response
```

### Service Client Example

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class AddClient(Node):
    def __init__(self):
        super().__init__('add_client')
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request(self, a, b):
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        future = self.client.call_async(request)
        return future
```

## Quality of Service (QoS)

ROS 2 provides Quality of Service settings to control communication behavior:

- **Reliability**: Ensure delivery (reliable) vs. best effort
- **Durability**: Keep last N messages vs. volatile
- **History**: Keep all messages vs. only new ones

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

qos_profile = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE
)
```

## Practical Application in Humanoid Robots

In humanoid robot systems, these communication patterns work together:

1. **Voice Input**: Microphone node publishes audio to speech recognition topic
2. **Speech Recognition**: Whisper node subscribes to audio, publishes text commands
3. **Command Processing**: LLM planner receives text, uses service to plan actions
4. **Action Execution**: Navigation nodes subscribe to action commands and execute them

This architecture enables the vision-language-action pipeline that allows voice commands to control robot behavior.

## Best Practices

- Keep nodes focused on single responsibilities
- Use appropriate QoS settings for your use case
- Implement proper error handling and logging
- Design topics with clear, descriptive names
- Use services for operations that require responses