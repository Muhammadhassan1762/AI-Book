---
sidebar_position: 2
---

# rclpy Integration

## Connecting AI Decision Logic to Robot Control

This section covers the technical implementation of connecting AI systems with robot controllers using rclpy. We'll explore practical patterns for integrating AI models with ROS 2 systems.

## Advanced Node Patterns

### Async/Await Pattern for AI Integration

For AI models that may take time to process, using async patterns can improve responsiveness:

```python
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

class AsyncAIProcessorNode(Node):
    def __init__(self):
        super().__init__('async_ai_processor')

        # Create a callback group for async operations
        self.ai_callback_group = MutuallyExclusiveCallbackGroup()

        # Subscription to commands
        self.command_sub = self.create_subscription(
            String,
            'ai_commands',
            self.async_command_callback,
            10,
            callback_group=self.ai_callback_group
        )

        # Publisher for results
        self.result_pub = self.create_publisher(
            String,
            'ai_results',
            10
        )

        # Thread pool for AI processing
        self.executor = ThreadPoolExecutor(max_workers=2)

    def async_command_callback(self, msg):
        """Handle command asynchronously to avoid blocking"""
        # Run AI processing in a separate thread
        future = asyncio.run_coroutine_threadsafe(
            self.process_command_async(msg.data),
            asyncio.new_event_loop()
        )

    async def process_command_async(self, command):
        """Process command asynchronously using AI model"""
        # Simulate AI processing (in real implementation, this would call your AI model)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.call_ai_model,
            command
        )

        # Publish result
        result_msg = String()
        result_msg.data = result
        self.result_pub.publish(result_msg)

    def call_ai_model(self, command):
        """Simulate calling an AI model - in practice, this would be your actual AI call"""
        # This is where you'd integrate with your AI model
        # e.g., OpenAI API, local LLM, vision model, etc.
        return f"Processed: {command}"
```

## Service-Based AI Integration

For synchronous AI processing where you need to wait for results:

```python
from example_interfaces.srv import Trigger
from std_msgs.msg import String

class AIServiceNode(Node):
    def __init__(self):
        super().__init__('ai_service_node')

        # Create service for AI processing
        self.ai_service = self.create_service(
            Trigger,
            'process_ai_request',
            self.process_ai_callback
        )

        # Publisher for detailed results
        self.result_publisher = self.create_publisher(
            String,
            'ai_detailed_results',
            10
        )

    def process_ai_callback(self, request, response):
        """Service callback for AI processing"""
        try:
            # Process AI request
            result = self.run_ai_processing()

            response.success = True
            response.message = f"AI processed successfully: {result}"

            # Publish detailed results
            result_msg = String()
            result_msg.data = result
            self.result_publisher.publish(result_msg)

        except Exception as e:
            response.success = False
            response.message = f"AI processing failed: {str(e)}"

        return response

    def run_ai_processing(self):
        """Run actual AI processing logic"""
        # Implement your AI model integration here
        return "AI processing result"
```

## Action-Based Integration for Long-Running Tasks

For AI tasks that take significant time, use ROS 2 actions:

```python
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from your_interfaces.action import AIProcess  # Custom action interface

class AIActionServer(Node):
    def __init__(self):
        super().__init__('ai_action_server')

        # Create action server with reentrant callback group
        self._action_server = ActionServer(
            self,
            AIProcess,
            'ai_process_action',
            self.execute_callback,
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

    def goal_callback(self, goal_request):
        """Accept or reject goals"""
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject cancel requests"""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """Execute the goal"""
        self.get_logger().info('Executing goal...')

        feedback_msg = AIProcess.Feedback()
        result = AIProcess.Result()

        try:
            # Simulate AI processing with feedback
            for i in range(0, 100, 10):
                # Check if goal was cancelled
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.get_logger().info('Goal canceled')
                    result.success = False
                    return result

                # Update feedback
                feedback_msg.progress = float(i)
                goal_handle.publish_feedback(feedback_msg)

                # Simulate AI processing step
                await asyncio.sleep(0.5)

            # Complete the goal
            goal_handle.succeed()
            result.success = True
            result.result_data = "AI processing completed successfully"

            self.get_logger().info('Goal succeeded')

        except Exception as e:
            goal_handle.abort()
            result.success = False
            result.result_data = f"AI processing failed: {str(e)}"

            self.get_logger().error(f'Goal failed: {str(e)}')

        return result
```

## Message Type Integration

ROS 2 provides many standard message types that are useful for AI integration:

### Sensor Data Processing

```python
from sensor_msgs.msg import Image, LaserScan
from cv_bridge import CvBridge
import cv2

class AIVisionNode(Node):
    def __init__(self):
        super().__init__('ai_vision_node')

        self.bridge = CvBridge()

        # Subscribe to camera images
        self.image_sub = self.create_subscription(
            Image,
            'camera/image_raw',
            self.image_callback,
            10
        )

        # Publisher for detection results
        self.detection_pub = self.create_publisher(
            String,
            'vision_detections',
            10
        )

    def image_callback(self, msg):
        """Process camera images with AI"""
        try:
            # Convert ROS Image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Process with AI vision model
            detections = self.process_vision(cv_image)

            # Publish results
            result_msg = String()
            result_msg.data = str(detections)
            self.detection_pub.publish(result_msg)

        except Exception as e:
            self.get_logger().error(f'Image processing error: {e}')

    def process_vision(self, cv_image):
        """Process image with AI model"""
        # Implement your vision AI here
        # e.g., object detection, pose estimation, etc.
        return {"objects": [], "confidence": 0.0}
```

## Parameter Integration

Use ROS 2 parameters to configure AI behavior:

```python
class ConfigurableAINode(Node):
    def __init__(self):
        super().__init__('configurable_ai_node')

        # Declare parameters with defaults
        self.declare_parameter('ai_model_name', 'gpt-4')
        self.declare_parameter('confidence_threshold', 0.7)
        self.declare_parameter('max_processing_time', 30.0)
        self.declare_parameter('enable_logging', True)

        # Get parameter values
        self.ai_model_name = self.get_parameter('ai_model_name').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.max_processing_time = self.get_parameter('max_processing_time').value
        self.enable_logging = self.get_parameter('enable_logging').value

        # Watch for parameter changes
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        """Handle parameter updates"""
        for param in params:
            if param.name == 'ai_model_name':
                self.ai_model_name = param.value
                self.get_logger().info(f'Updated AI model: {self.ai_model_name}')
            elif param.name == 'confidence_threshold':
                self.confidence_threshold = param.value
                self.get_logger().info(f'Updated confidence threshold: {self.confidence_threshold}')

        return SetParametersResult(successful=True)
```

## Error Handling and Safety

Implement robust error handling for AI-robot integration:

```python
class SafeAIIntegrationNode(Node):
    def __init__(self):
        super().__init__('safe_ai_integration')

        # Safety publishers
        self.emergency_stop_pub = self.create_publisher(
            Bool,
            'emergency_stop',
            10
        )

        # Error tracking
        self.error_count = 0
        self.max_errors = 5

        # Initialize AI with error handling
        self.initialize_ai_with_retry()

    def initialize_ai_with_retry(self, max_retries=3):
        """Initialize AI with retry logic"""
        for attempt in range(max_retries):
            try:
                # Initialize your AI model
                self.ai_model = self.create_ai_model()
                self.get_logger().info('AI model initialized successfully')
                return
            except Exception as e:
                self.get_logger().error(f'AI initialization failed (attempt {attempt + 1}): {e}')
                if attempt == max_retries - 1:
                    self.emergency_stop()
                    raise RuntimeError('Failed to initialize AI after multiple attempts')

    def safe_ai_call(self, input_data):
        """Call AI model with safety checks"""
        try:
            # Validate input
            if not self.validate_input(input_data):
                raise ValueError('Invalid input data')

            # Call AI model
            result = self.ai_model.process(input_data)

            # Validate output
            if not self.validate_output(result):
                raise ValueError('Invalid AI output')

            return result

        except Exception as e:
            self.error_count += 1
            self.get_logger().error(f'AI processing error: {e}')

            if self.error_count >= self.max_errors:
                self.get_logger().error('Too many errors, triggering safety measures')
                self.emergency_stop()

            return None

    def validate_input(self, input_data):
        """Validate AI input data"""
        # Implement input validation logic
        return True

    def validate_output(self, output_data):
        """Validate AI output data"""
        # Implement output validation logic
        return True

    def emergency_stop(self):
        """Trigger emergency stop"""
        stop_msg = Bool()
        stop_msg.data = True
        self.emergency_stop_pub.publish(stop_msg)
        self.get_logger().warn('Emergency stop triggered!')
```

## Performance Optimization

For efficient AI-robot integration:

### Message Throttling

```python
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy

class OptimizedAINode(Node):
    def __init__(self):
        super().__init__('optimized_ai_node')

        # Use appropriate QoS for different data types
        sensor_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST
        )

        control_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Subscriptions with optimized QoS
        self.sensor_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.sensor_callback,
            sensor_qos
        )
```

## Integration Patterns Summary

1. **Async Processing**: Use for non-blocking AI calls
2. **Service Calls**: Use for synchronous, request-response patterns
3. **Actions**: Use for long-running AI tasks
4. **Parameter Integration**: Use for dynamic AI configuration
5. **Safety First**: Always implement error handling and safety measures
6. **Performance**: Optimize message rates and processing

These patterns enable robust integration between AI systems and robot controllers, forming the foundation for intelligent humanoid robot behavior.