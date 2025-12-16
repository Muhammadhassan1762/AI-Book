# Data Model: The Robotic Nervous System (ROS 2)

## ROS 2 Node Entity
- **Name**: Node identifier string
- **Fields**:
  - node_id: unique identifier for the node
  - node_name: human-readable name of the node
  - publishers: list of topics the node publishes to
  - subscribers: list of topics the node subscribes to
  - services: list of services the node provides
  - clients: list of services the node calls
- **Relationships**: Connects to other nodes through topics and services
- **Validation rules**: Node name must follow ROS naming conventions

## ROS 2 Topic Entity
- **Name**: Topic identifier string
- **Fields**:
  - topic_name: name of the topic
  - message_type: type of message published/subscribed
  - publishers: list of nodes publishing to this topic
  - subscribers: list of nodes subscribing to this topic
- **Relationships**: Connects publisher nodes to subscriber nodes
- **Validation rules**: Topic names must follow ROS naming conventions

## ROS 2 Service Entity
- **Name**: Service identifier string
- **Fields**:
  - service_name: name of the service
  - request_type: type of request message
  - response_type: type of response message
  - provider: node providing the service
  - clients: list of nodes using the service
- **Relationships**: Connects service provider to service clients
- **Validation rules**: Service names must follow ROS naming conventions

## URDF Robot Model Entity
- **Name**: Robot model identifier
- **Fields**:
  - robot_name: name of the robot
  - links: list of physical components
  - joints: list of connections between links
  - materials: list of visual materials
  - gazebo_extensions: simulation-specific configurations
- **Relationships**: Links connected through joints in hierarchical structure
- **Validation rules**: Must have at least one base link and valid joint connections

## Link Entity
- **Name**: Physical component of robot
- **Fields**:
  - link_name: name of the link
  - visual: visual representation properties
  - collision: collision detection properties
  - inertial: mass and inertia properties
- **Relationships**: Connected to other links through joints
- **Validation rules**: Must have valid geometric shapes for visual and collision

## Joint Entity
- **Name**: Connection between two links
- **Fields**:
  - joint_name: name of the joint
  - joint_type: type of joint (revolute, prismatic, etc.)
  - parent_link: link that is the parent in the hierarchy
  - child_link: link that is the child in the hierarchy
  - limits: movement constraints for the joint
- **Relationships**: Connects parent and child links
- **Validation rules**: Must have valid parent and child links

## ROS 2 Message Entity
- **Name**: Data structure for communication
- **Fields**:
  - message_type: type definition of the message
  - fields: list of data fields in the message
  - field_types: types of each field
- **Relationships**: Used by topics and services for data exchange
- **Validation rules**: Must conform to ROS message specification

## rclpy Node Implementation Entity
- **Name**: Python node implementation
- **Fields**:
  - node_class: Python class implementing the node
  - initialization_params: parameters for node creation
  - callback_functions: functions handling messages/services
  - executor: ROS executor managing node execution
- **Relationships**: Instantiates ROS 2 Node entity at runtime
- **Validation rules**: Must inherit from rclpy.node.Node