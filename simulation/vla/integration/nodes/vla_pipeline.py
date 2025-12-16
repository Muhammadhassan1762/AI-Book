#!/usr/bin/env python3
"""
VLA Integration Pipeline Node for VLA System

This node orchestrates the complete Vision-Language-Action pipeline,
coordinating between Whisper, LLM planner, and execution components.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction, VLAStatus
from vla_interfaces.srv import ProcessCommand, PlanActions, ValidateSafety
from std_msgs.msg import String, Bool
from action_msgs.msg import GoalStatus
import time
from enum import Enum
from typing import List, Dict, Any, Optional
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor


class PipelineState(Enum):
    """States of the VLA pipeline"""
    IDLE = "IDLE"
    PROCESSING_COMMAND = "PROCESSING_COMMAND"
    PLANNING_ACTIONS = "PLANNING_ACTIONS"
    VALIDATING_SAFETY = "VALIDATING_SAFETY"
    EXECUTING_ACTIONS = "EXECUTING_ACTIONS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class VLAPipelineNode(Node):
    def __init__(self):
        super().__init__('vla_pipeline_node')

        # Declare parameters
        self.declare_parameter('enable_pipeline', True)
        self.declare_parameter('pipeline_mode', 'auto')
        self.declare_parameter('execution_timeout', 300.0)
        self.declare_parameter('max_replanning_attempts', 3)
        self.declare_parameter('safety_check_enabled', True)
        self.declare_parameter('safety_confirmation_required', False)
        self.declare_parameter('safety_threshold', 0.8)
        self.declare_parameter('command_input_topic', '/vla/command')
        self.declare_parameter('action_sequence_input_topic', '/vla/action_sequence')
        self.declare_parameter('status_output_topic', '/vla/status')
        self.declare_parameter('error_output_topic', '/vla/error')
        self.declare_parameter('process_command_service', '/vla/process_command')
        self.declare_parameter('validate_safety_service', '/vla/validate_safety')
        self.declare_parameter('execute_pipeline_service', '/vla/execute_pipeline')
        self.declare_parameter('enable_context_tracking', True)
        self.declare_parameter('context_retention_time', 300.0)
        self.declare_parameter('enable_context_sharing', True)
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')
        self.declare_parameter('enable_performance_monitoring', True)
        self.declare_parameter('performance_log_interval', 10.0)

        # Get parameters
        self.enable_pipeline = self.get_parameter('enable_pipeline').value
        self.pipeline_mode = self.get_parameter('pipeline_mode').value
        self.execution_timeout = self.get_parameter('execution_timeout').value
        self.max_replanning_attempts = self.get_parameter('max_replanning_attempts').value
        self.safety_check_enabled = self.get_parameter('safety_check_enabled').value
        self.safety_confirmation_required = self.get_parameter('safety_confirmation_required').value
        self.safety_threshold = self.get_parameter('safety_threshold').value
        command_input_topic = self.get_parameter('command_input_topic').value
        action_sequence_input_topic = self.get_parameter('action_sequence_input_topic').value
        status_output_topic = self.get_parameter('status_output_topic').value
        error_output_topic = self.get_parameter('error_output_topic').value
        process_command_service = self.get_parameter('process_command_service').value
        validate_safety_service = self.get_parameter('validate_safety_service').value
        execute_pipeline_service = self.get_parameter('execute_pipeline_service').value
        self.enable_context_tracking = self.get_parameter('enable_context_tracking').value
        self.context_retention_time = self.get_parameter('context_retention_time').value
        self.enable_context_sharing = self.get_parameter('enable_context_sharing').value
        self.enable_debug = self.get_parameter('enable_debug').value
        self.enable_performance_monitoring = self.get_parameter('enable_performance_monitoring').value
        self.performance_log_interval = self.get_parameter('performance_log_interval').value

        # Initialize pipeline state
        self.current_state = PipelineState.IDLE
        self.current_action_index = 0
        self.current_action_sequence = None
        self.replanning_attempts = 0
        self.pipeline_start_time = None
        self.context = {}
        self.action_status = {}  # Track status of each action

        # Create subscribers and publishers
        self.command_sub = self.create_subscription(
            VLACommand,
            command_input_topic,
            self.command_callback,
            10
        )

        self.action_sequence_sub = self.create_subscription(
            VLAActionSequence,
            action_sequence_input_topic,
            self.action_sequence_callback,
            10
        )

        self.status_pub = self.create_publisher(
            VLAStatus,
            status_output_topic,
            10
        )

        self.error_pub = self.create_publisher(
            String,
            error_output_topic,
            10
        )

        # Create service clients
        self.process_command_client = self.create_client(
            ProcessCommand,
            process_command_service
        )
        self.validate_safety_client = self.create_client(
            ValidateSafety,
            validate_safety_service
        )

        # Create service server
        self.execute_pipeline_srv = self.create_service(
            ProcessCommand,
            execute_pipeline_service,
            self.execute_pipeline_callback
        )

        # Wait for services to be available
        self.get_logger().info('Waiting for services...')
        while not self.process_command_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Process command service not available, waiting...')
        while not self.validate_safety_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Validate safety service not available, waiting...')

        # Timer for performance monitoring
        if self.enable_performance_monitoring:
            self.performance_timer = self.create_timer(
                self.performance_log_interval,
                self.performance_monitor_callback
            )

        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=3)

        self.get_logger().info('VLA Integration Pipeline node initialized')

    def command_callback(self, msg):
        """Callback for VLA command input"""
        if not self.enable_pipeline:
            self.get_logger().warn('Pipeline is disabled, ignoring command')
            return

        self.get_logger().info(f'Received command: "{msg.command_text}" (confidence: {msg.confidence_score:.2f})')

        # Update state and publish status
        self.current_state = PipelineState.PROCESSING_COMMAND
        self.publish_status('Processing command', 0.0)

        # Process the command through the pipeline
        future = asyncio.run_coroutine_threadsafe(
            self.process_command_pipeline(msg),
            asyncio.new_event_loop()
        )

    def action_sequence_callback(self, msg):
        """Callback for action sequence input"""
        self.get_logger().info(f'Received action sequence with {len(msg.actions)} actions')

        # Update state and publish status
        self.current_state = PipelineState.VALIDATING_SAFETY
        self.publish_status('Validating safety of action sequence', 10.0)

        # Process the action sequence
        future = asyncio.run_coroutine_threadsafe(
            self.process_action_sequence_pipeline(msg),
            asyncio.new_event_loop()
        )

    async def process_command_pipeline(self, command_msg):
        """Process a command through the full VLA pipeline"""
        try:
            self.pipeline_start_time = time.time()
            self.replanning_attempts = 0  # Reset replanning attempts for new pipeline

            # Step 1: Process command (if needed)
            self.current_state = PipelineState.PROCESSING_COMMAND
            self.publish_status('Processing command', 5.0)

            # If confidence is too low, we might want to request clarification
            if command_msg.confidence_score < 0.7:
                self.get_logger().warn(f'Low confidence command: {command_msg.confidence_score}')
                # In a real system, we might request clarification here

            # Step 2: Plan actions using LLM
            self.current_state = PipelineState.PLANNING_ACTIONS
            self.publish_status('Planning actions with LLM', 25.0)

            action_sequence = await self.call_llm_planner(command_msg)

            if not action_sequence or len(action_sequence.actions) == 0:
                self.get_logger().error('No action sequence generated')
                self.current_state = PipelineState.ERROR
                self.publish_status('Failed to generate action sequence', 0.0, error_message='No actions generated')
                return

            # Step 3: Validate safety
            self.current_state = PipelineState.VALIDATING_SAFETY
            self.publish_status('Validating safety of planned actions', 50.0)

            is_safe, requires_confirmation, issues = await self.validate_safety(action_sequence)

            if not is_safe:
                self.get_logger().error(f'Safety validation failed: {issues}')
                self.current_state = PipelineState.ERROR
                self.publish_status('Safety validation failed', 0.0, error_message=f'Safety issues: {issues}')
                return

            if requires_confirmation and self.safety_confirmation_required:
                self.get_logger().info('Safety confirmation required')
                # In a real system, we would wait for user confirmation here

            # Step 4: Execute actions
            self.current_state = PipelineState.EXECUTING_ACTIONS
            self.publish_status('Executing action sequence', 75.0)

            execution_success = await self.execute_action_sequence(action_sequence)

            if execution_success:
                self.current_state = PipelineState.COMPLETED
                self.publish_status('Pipeline completed successfully', 100.0)
                self.get_logger().info('VLA pipeline completed successfully')
            else:
                self.get_logger().error('Action sequence execution failed')
                self.current_state = PipelineState.ERROR
                self.publish_status('Action execution failed', 0.0, error_message='Action execution failed')

        except Exception as e:
            self.get_logger().error(f'Error in command pipeline: {e}')
            self.current_state = PipelineState.ERROR
            self.publish_status('Pipeline error', 0.0, error_message=str(e))

    async def process_action_sequence_pipeline(self, action_sequence_msg):
        """Process an action sequence directly"""
        try:
            self.pipeline_start_time = time.time()
            self.replanning_attempts = 0  # Reset replanning attempts for new pipeline

            # Step 1: Validate safety
            self.current_state = PipelineState.VALIDATING_SAFETY
            self.publish_status('Validating safety of action sequence', 50.0)

            is_safe, requires_confirmation, issues = await self.validate_safety(action_sequence_msg)

            if not is_safe:
                self.get_logger().error(f'Safety validation failed: {issues}')
                self.current_state = PipelineState.ERROR
                self.publish_status('Safety validation failed', 0.0, error_message=f'Safety issues: {issues}')
                return

            if requires_confirmation and self.safety_confirmation_required:
                self.get_logger().info('Safety confirmation required')
                # In a real system, we would wait for user confirmation here

            # Step 2: Execute actions
            self.current_state = PipelineState.EXECUTING_ACTIONS
            self.publish_status('Executing action sequence', 75.0)

            execution_success = await self.execute_action_sequence(action_sequence_msg)

            if execution_success:
                self.current_state = PipelineState.COMPLETED
                self.publish_status('Pipeline completed successfully', 100.0)
                self.get_logger().info('Action sequence executed successfully')
            else:
                self.get_logger().error('Action sequence execution failed')
                self.current_state = PipelineState.ERROR
                self.publish_status('Action execution failed', 0.0, error_message='Action execution failed')

        except Exception as e:
            self.get_logger().error(f'Error in action sequence pipeline: {e}')
            self.current_state = PipelineState.ERROR
            self.publish_status('Pipeline error', 0.0, error_message=str(e))

    async def call_llm_planner(self, command_msg):
        """Call the LLM planner service asynchronously"""
        loop = asyncio.get_event_loop()

        # For now, we'll simulate by creating a simple action sequence
        # In a real system, this would call the PlanActions service
        action_sequence = VLAActionSequence()
        action_sequence.status = 'PENDING'
        action_sequence.safety_level = 'NORMAL'
        action_sequence.estimated_duration.sec = 120
        action_sequence.estimated_duration.nanosec = 0

        # Create a simple action based on the command
        action = VLAAction()
        if 'go' in command_msg.command_text.lower() or 'move' in command_msg.command_text.lower():
            action.action_type = 'NAVIGATION'
            action.action_parameters = ['location=kitchen']  # Simplified
        elif 'pick' in command_msg.command_text.lower() or 'grasp' in command_msg.command_text.lower():
            action.action_type = 'MANIPULATION'
            action.action_parameters = ['object_type=cup']  # Simplified
        else:
            action.action_type = 'SYSTEM'
            action.action_parameters = ['text=Command received']

        action.priority = 1
        action.timeout.sec = 30
        action.timeout.nanosec = 0
        action.dependencies = []

        action_sequence.actions.append(action)

        return action_sequence

    async def validate_safety(self, action_sequence):
        """Validate the safety of an action sequence"""
        if not self.safety_check_enabled:
            return True, False, []

        # For now, we'll simulate safety validation
        # In a real system, this would call the ValidateSafety service
        issues = []
        requires_confirmation = False

        # Check each action for safety
        for i, action in enumerate(action_sequence.actions):
            if action.action_type == 'NAVIGATION':
                # Check if navigation target is valid
                pass
            elif action.action_type == 'MANIPULATION':
                # Check if manipulation is safe
                pass
            elif action.action_type == 'PERCEPTION':
                # Check if perception is safe
                pass

        is_safe = len(issues) == 0
        return is_safe, requires_confirmation, issues

    async def execute_action_sequence(self, action_sequence):
        """Execute an action sequence"""
        self.current_action_sequence = action_sequence
        self.current_action_index = 0

        for i, action in enumerate(action_sequence.actions):
            self.current_action_index = i
            progress = 75.0 + (25.0 * (i + 1) / len(action_sequence.actions))
            self.publish_status(f'Executing action {i+1}/{len(action_sequence.actions)}: {action.action_type}', progress)

            # Execute the action (simulated)
            success = await self.execute_single_action(action)

            if not success:
                self.get_logger().warn(f'Action {i} failed: {action.action_type}')
                # In a real system, we might try to replan or handle the failure
                return False

            # Update progress
            progress = 75.0 + (25.0 * (i + 1) / len(action_sequence.actions))
            self.publish_status(f'Completed action {i+1}/{len(action_sequence.actions)}', progress)

        return True

    async def execute_single_action(self, action):
        """Execute a single action with obstacle detection and replanning capability"""
        # In a real system, this would interface with the actual robot
        # For simulation, we'll simulate execution and potential obstacles
        self.get_logger().info(f'Executing action: {action.action_type} with params {action.action_parameters}')

        try:
            # Simulate action execution time based on timeout
            execution_time = min(action.timeout.sec + (action.timeout.nanosec / 1e9), 5.0)  # Cap at 5 seconds for simulation

            # Simulate potential obstacles during navigation
            if action.action_type == 'NAVIGATION':
                # Simulate a 20% chance of encountering an obstacle during navigation
                import random
                if random.random() < 0.2:  # 20% chance
                    self.get_logger().warn('Obstacle detected during navigation!')

                    # Attempt replanning
                    if self.replanning_attempts < self.max_replanning_attempts:
                        self.replanning_attempts += 1
                        self.get_logger().info(f'Attempting replan (attempt {self.replanning_attempts})')

                        # In a real system, this would call the planner to generate a new path
                        # For simulation, we'll just continue after a delay
                        await asyncio.sleep(2.0)  # Time to "replan"

                        # Retry the same action
                        return await self.execute_single_action(action)
                    else:
                        self.get_logger().error('Max replanning attempts reached')
                        return False

            await asyncio.sleep(execution_time)  # Simulate execution time

            # For now, return success
            # In a real system, this would check actual execution results
            return True

        except Exception as e:
            self.get_logger().error(f'Error executing action: {e}')
            return False

    def execute_pipeline_callback(self, request, response):
        """Service callback to execute pipeline directly"""
        try:
            # Create a command message from the request
            cmd_msg = VLACommand()
            cmd_msg.command_text = request.raw_command
            cmd_msg.confidence_score = request.audio_confidence
            cmd_msg.intent = 'GENERAL_COMMAND'  # Will be inferred
            cmd_msg.parameters = []
            cmd_msg.timestamp = self.get_clock().now().to_msg()

            # Process through pipeline
            future = asyncio.run_coroutine_threadsafe(
                self.process_command_pipeline(cmd_msg),
                asyncio.new_event_loop()
            )

            # For the service response, we return immediately
            response.success = True
            response.processed_command = request.raw_command
            response.intent = 'GENERAL_COMMAND'
            response.parameters = []
            response.error_message = ""
            response.error_code = 0

        except Exception as e:
            response.success = False
            response.error_message = f"Pipeline execution error: {e}"
            response.error_code = 1

        return response

    def publish_status(self, current_action="", progress=0.0, error_message=""):
        """Publish status update"""
        status_msg = VLAStatus()
        status_msg.current_state = self.current_state.value
        status_msg.current_action = current_action
        status_msg.progress_percentage = float(progress)
        status_msg.timestamp = self.get_clock().now().to_msg()
        status_msg.error_message = error_message
        status_msg.recent_actions = []  # Will be populated based on context

        self.status_pub.publish(status_msg)

    def performance_monitor_callback(self):
        """Monitor and log performance metrics"""
        if self.pipeline_start_time:
            elapsed_time = time.time() - self.pipeline_start_time
            self.get_logger().info(f'Pipeline performance: elapsed={elapsed_time:.2f}s, state={self.current_state.value}')

    def get_context(self, key: str, default=None):
        """Get value from context"""
        if not self.enable_context_tracking:
            return default
        return self.context.get(key, default)

    def set_context(self, key: str, value: Any):
        """Set value in context"""
        if self.enable_context_tracking:
            self.context[key] = value

    def clear_context(self):
        """Clear context"""
        if self.enable_context_tracking:
            self.context.clear()


def main(args=None):
    rclpy.init(args=args)
    node = VLAPipelineNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.executor.shutdown(wait=True)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()