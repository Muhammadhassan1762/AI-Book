---
sidebar_position: 2
---

# Nodes, Topics, Services, and Actions

## Understanding ROS 2 Communication Patterns

In ROS 2, communication between different parts of your robot software happens through several distinct patterns. Understanding these patterns is crucial for building effective robot systems. Let's explore each of these fundamental concepts.

## Nodes: The Building Blocks of ROS 2

### What is a Node?

A **node** is a process that performs computation in ROS 2. It's the fundamental unit of a ROS program that communicates with other nodes. Think of nodes as the individual organs in a robot's nervous system - each one performs a specific function but works together with others to create complex behavior.

### Key Characteristics of Nodes

- **Specialized Function**: Each node typically performs one specific task (e.g., sensor processing, motor control, path planning)
- **Communication Hub**: Nodes communicate with other nodes through topics, services, and actions
- **Process-based**: Each node runs as a separate process, providing isolation between different components
- **Named**: Every node has a unique name within the ROS graph

### Creating Nodes

In our examples, we've already seen two nodes:
- `basic_publisher`: A node that sends messages to other nodes
- `basic_subscriber`: A node that receives messages from other nodes

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('node_name')  # Initialize with a unique name
        # Add functionality here
```

## Topics: Publisher-Subscriber Communication

### What is a Topic?

A **topic** is a named bus over which nodes exchange messages. It implements a publisher-subscriber communication pattern where publishers send messages to a topic and subscribers receive messages from that topic. This is the most common way nodes communicate in ROS 2.

### Key Characteristics of Topics

- **Asynchronous**: Publishers and subscribers don't need to be synchronized in time
- **Many-to-Many**: Multiple publishers can send to a topic, and multiple subscribers can receive from it
- **Data-Driven**: Topics are typically used for continuous data streams (sensor data, motor commands, etc.)
- **Message Types**: Each topic has a specific message type that defines the structure of data sent

### Example: The 'chatter' Topic

In our basic example, the publisher and subscriber communicate through a topic named 'chatter':

```python
# Publisher creates a publisher for the 'chatter' topic
self.publisher_ = self.create_publisher(String, 'chatter', 10)

# Subscriber creates a subscription to the 'chatter' topic
self.subscription = self.create_subscription(
    String,
    'chatter',
    self.listener_callback,
    10)
```

## Services: Request-Response Communication

### What is a Service?

A **service** provides a request-response communication pattern. A client sends a request to a service server, which processes the request and sends back a response. This is synchronous communication, meaning the client waits for the response.

### Key Characteristics of Services

- **Synchronous**: The client waits for the server to respond
- **One-to-One**: One client talks to one server at a time
- **Request-Response**: Client sends request, server sends response
- **Stateless**: Each service call is independent of others

### When to Use Services

Services are ideal for:
- Operations that have a clear start and end
- Requesting specific information (e.g., "What's the robot's current position?")
- Operations that modify system state (e.g., "Set robot to safe mode")

## Actions: Goal-Based Communication

### What is an Action?

An **action** is a more complex communication pattern that combines features of both topics and services. It's used for long-running tasks that have goals, feedback, and results. Actions are perfect for tasks that take time to complete and need to provide status updates.

### Key Characteristics of Actions

- **Long-Running**: Designed for tasks that take time to complete
- **Feedback**: Provides continuous feedback during execution
- **Cancelation**: Goals can be canceled before completion
- **Goal-Result**: Client sends a goal, receives result when complete

### When to Use Actions

Actions are ideal for:
- Navigation tasks ("Go to position X")
- Manipulation tasks ("Pick up object")
- Calibration procedures
- Any task that requires progress tracking

## Communication Pattern Comparison

| Pattern | Type | Use Case | Example |
|---------|------|----------|---------|
| Topics | Publisher-Subscriber | Continuous data streams | Sensor data, motor commands |
| Services | Request-Response | Short, discrete operations | Get robot status, save map |
| Actions | Goal-Based | Long-running tasks with feedback | Navigation, manipulation |

## The ROS 2 Communication Ecosystem

These communication patterns work together to create a flexible and robust system:

1. **Sensors** typically publish data to topics
2. **Controllers** subscribe to sensor topics and publish commands to actuator topics
3. **Planning modules** might use services to request specific information
4. **High-level behaviors** might use actions to coordinate complex tasks

Understanding these patterns is crucial for designing effective robot software architectures. Each pattern serves a specific purpose and choosing the right one for your use case will make your robot more efficient and reliable.

## Summary

- **Nodes** are the basic computational units in ROS 2
- **Topics** enable asynchronous, many-to-many communication
- **Services** provide synchronous, request-response communication
- **Actions** handle long-running tasks with feedback and cancelation

In the next section, we'll dive deeper into the publisher-subscriber model and see how it enables robot control.