#!/usr/bin/env python3
"""
LLM Cognitive Planner Node for VLA System

This node uses a Large Language Model to convert natural language commands
into sequences of ROS 2 actions for the Vision-Language-Action pipeline.
"""

import rclpy
from rclpy.node import Node
import openai
import json
import time
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction, VLAStatus
from vla_interfaces.srv import PlanActions, ProcessCommand
from std_msgs.msg import String
import asyncio
from concurrent.futures import ThreadPoolExecutor


class CognitivePlannerNode(Node):
    def __init__(self):
        super().__init__('llm_planner_node')

        # Declare parameters
        self.declare_parameter('llm_provider', 'openai')
        self.declare_parameter('model_name', 'gpt-4o')
        self.declare_parameter('api_key', '')
        self.declare_parameter('base_url', '')
        self.declare_parameter('ollama_host', 'localhost')
        self.declare_parameter('ollama_port', 11434)
        self.declare_parameter('max_tokens', 1000)
        self.declare_parameter('temperature', 0.3)
        self.declare_parameter('timeout', 30.0)
        self.declare_parameter('max_retries', 3)
        self.declare_parameter('enable_context_awareness', True)
        self.declare_parameter('enable_safety_validation', True)
        self.declare_parameter('enable_multi_step_planning', True)
        self.declare_parameter('input_command_topic', '/vla/command')
        self.declare_parameter('output_action_sequence_topic', '/vla/action_sequence')
        self.declare_parameter('status_topic', '/vla/status')
        self.declare_parameter('plan_actions_service', '/vla/plan_actions')
        self.declare_parameter('validate_safety_service', '/vla/validate_safety')
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')

        # Get parameters
        self.llm_provider = self.get_parameter('llm_provider').value
        self.model_name = self.get_parameter('model_name').value
        self.api_key = self.get_parameter('api_key').value or self.get_openai_api_key()
        self.base_url = self.get_parameter('base_url').value
        self.ollama_host = self.get_parameter('ollama_host').value
        self.ollama_port = self.get_parameter('ollama_port').value
        self.max_tokens = self.get_parameter('max_tokens').value
        self.temperature = self.get_parameter('temperature').value
        self.timeout = self.get_parameter('timeout').value
        self.max_retries = self.get_parameter('max_retries').value
        self.enable_context_awareness = self.get_parameter('enable_context_awareness').value
        self.enable_safety_validation = self.get_parameter('enable_safety_validation').value
        self.enable_multi_step_planning = self.get_parameter('enable_multi_step_planning').value
        input_command_topic = self.get_parameter('input_command_topic').value
        output_action_sequence_topic = self.get_parameter('output_action_sequence_topic').value
        status_topic = self.get_parameter('status_topic').value
        plan_actions_service = self.get_parameter('plan_actions_service').value
        self.enable_debug = self.get_parameter('enable_debug').value

        # Initialize LLM client
        self.initialize_llm_client()

        # Create subscribers and publishers
        self.command_sub = self.create_subscription(
            VLACommand,
            input_command_topic,
            self.command_callback,
            10
        )

        self.action_sequence_pub = self.create_publisher(
            VLAActionSequence,
            output_action_sequence_topic,
            10
        )

        self.status_pub = self.create_publisher(
            VLAStatus,
            status_topic,
            10
        )

        # Create service server
        self.plan_actions_srv = self.create_service(
            PlanActions,
            plan_actions_service,
            self.plan_actions_callback
        )

        # Thread pool for async LLM calls
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.get_logger().info('LLM Cognitive Planner node initialized')

    def get_openai_api_key(self):
        """Get API key from environment variable if not provided in config"""
        import os
        return os.getenv('OPENAI_API_KEY', '')

    def initialize_llm_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.llm_provider == 'openai':
            if not self.api_key:
                self.get_logger().warn('No OpenAI API key provided. Set OPENAI_API_KEY environment variable.')
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url if self.base_url else None)
            self.get_logger().info(f'Initialized OpenAI client with model: {self.model_name}')
        elif self.llm_provider == 'ollama':
            # For Ollama, we'll use the OpenAI-compatible API
            base_url = f"http://{self.ollama_host}:{self.ollama_port}"
            self.client = openai.OpenAI(base_url=base_url, api_key="ollama")
            self.get_logger().info(f'Initialized Ollama client at {base_url} with model: {self.model_name}')
        else:
            self.get_logger().error(f'Unsupported LLM provider: {self.llm_provider}')
            raise ValueError(f'Unsupported LLM provider: {self.llm_provider}')

    def command_callback(self, msg):
        """Callback for VLA command input"""
        self.get_logger().info(f'Received command: "{msg.command_text}" (confidence: {msg.confidence_score:.2f})')

        # Publish status update
        status_msg = self.create_status_message('PLANNING', f'Processing command: {msg.command_text}', 0.0)
        self.status_pub.publish(status_msg)

        # Plan actions asynchronously
        future = asyncio.run_coroutine_threadsafe(
            self.plan_actions_async(msg.command_text, msg.intent, msg.parameters),
            asyncio.new_event_loop()
        )

    async def plan_actions_async(self, command_text, intent, parameters):
        """Asynchronously plan actions using LLM"""
        try:
            action_sequence = await self.call_llm_for_planning(command_text, intent, parameters)

            if action_sequence:
                # Publish the action sequence
                self.action_sequence_pub.publish(action_sequence)

                # Publish completion status
                status_msg = self.create_status_message('COMPLETED', f'Generated {len(action_sequence.actions)} actions', 100.0)
                self.status_pub.publish(status_msg)

                self.get_logger().info(f'Generated action sequence with {len(action_sequence.actions)} actions')
            else:
                # Publish error status
                status_msg = self.create_status_message('ERROR', 'Failed to generate action sequence', 0.0)
                self.status_pub.publish(status_msg)
                self.get_logger().error('Failed to generate action sequence')

        except Exception as e:
            self.get_logger().error(f'Error in async planning: {e}')
            status_msg = self.create_status_message('ERROR', f'Planning error: {str(e)}', 0.0)
            self.status_pub.publish(status_msg)

    def plan_actions_callback(self, request, response):
        """Service callback to plan actions from command"""
        try:
            # Create a temporary command message from the request
            command_msg = VLACommand()
            command_msg.command_text = request.command_text
            command_msg.intent = request.intent
            command_msg.parameters = request.parameters

            # Plan actions synchronously for the service call
            action_sequence = self.plan_actions_sync(
                command_msg.command_text,
                command_msg.intent,
                command_msg.parameters
            )

            if action_sequence:
                response.success = True
                response.action_sequence = action_sequence
                response.error_message = ""
                response.error_code = 0
            else:
                response.success = False
                response.error_message = "Failed to generate action sequence"
                response.error_code = 1  # General error

        except Exception as e:
            response.success = False
            response.error_message = f"Error planning actions: {e}"
            response.error_code = 1  # General error

        return response

    def plan_actions_sync(self, command_text, intent, parameters):
        """Synchronously plan actions using LLM"""
        try:
            # Prepare the prompt for the LLM
            prompt = self.create_planning_prompt(command_text, intent, parameters)

            # Call the LLM with retry logic
            for attempt in range(self.max_retries):
                try:
                    completion = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": self.get_system_prompt()},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        timeout=self.timeout
                    )

                    # Parse the response
                    response_text = completion.choices[0].message.content.strip()
                    action_sequence = self.parse_llm_response(response_text)

                    if action_sequence:
                        return action_sequence
                    else:
                        self.get_logger().warn(f'Attempt {attempt + 1}: Failed to parse LLM response')

                except Exception as e:
                    self.get_logger().warn(f'Attempt {attempt + 1} failed: {e}')
                    if attempt == self.max_retries - 1:
                        raise e
                    time.sleep(1)  # Wait before retrying

        except Exception as e:
            self.get_logger().error(f'Error planning actions: {e}')
            return None

    async def call_llm_for_planning(self, command_text, intent, parameters):
        """Asynchronously call LLM for action planning"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.plan_actions_sync,
            command_text,
            intent,
            parameters
        )

    def create_planning_prompt(self, command_text, intent, parameters):
        """Create the prompt for action planning"""
        prompt = f"""
        Convert the following natural language command into a sequence of ROS 2 actions for a humanoid robot.

        Command: "{command_text}"
        Intent: {intent}
        Parameters: {parameters}

        Available Action Types:
        - NAVIGATION: Navigate to a location or object
          Parameters: location, frame_id, object_id, approach_distance
          Examples: "location=kitchen", "object_id=red_cup_001"

        - PERCEPTION: Detect or locate objects in the environment
          Parameters: object_types, detection_range, object_type, search_area
          Examples: "object_types=['cup', 'ball']", "object_type=red_cup"

        - MANIPULATION: Grasp, place, or manipulate objects
          Parameters: object_id, grasp_type, target_location, placement_type
          Examples: "object_id=red_cup_001", "target_location=table"

        - SYSTEM: Wait, speak, or system control actions
          Parameters: duration, text, voice_type
          Examples: "duration=5.0", "text=Task completed"

        Please respond with a JSON array of actions in the following format:
        {{
          "actions": [
            {{
              "action_type": "NAVIGATION",
              "action_parameters": ["location=kitchen"],
              "priority": 1,
              "timeout": 30.0,
              "dependencies": []
            }}
          ]
        }}

        Make sure the action sequence is logical, executable, and achieves the command goal.
        """

        return prompt

    def get_system_prompt(self):
        """Get the system prompt for the LLM"""
        return """
        You are an expert in robotics and action planning. Your task is to convert natural language commands into sequences of executable actions for a humanoid robot. The robot operates in a structured environment with known locations and objects.

        Rules:
        1. Always return a valid JSON response
        2. Use only the action types provided: NAVIGATION, PERCEPTION, MANIPULATION, SYSTEM
        3. Include all required parameters for each action
        4. Ensure the action sequence is logical and achievable
        5. Consider dependencies between actions (e.g., detect object before grasping)
        6. Set appropriate priorities and timeouts
        7. If the command is ambiguous, ask for clarification through SYSTEM actions
        """

    def parse_llm_response(self, response_text):
        """Parse the LLM response into an action sequence"""
        try:
            # Try to find JSON in the response (in case LLM includes extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                # If no JSON delimiters found, try to parse the whole response
                data = json.loads(response_text)

            # Create VLAActionSequence message
            action_sequence = VLAActionSequence()
            action_sequence.status = 'PENDING'
            action_sequence.safety_level = 'NORMAL'  # Will be updated by safety validator
            action_sequence.estimated_duration = 0.0  # Will be calculated based on actions

            if 'actions' in data and isinstance(data['actions'], list):
                for action_data in data['actions']:
                    action = VLAAction()
                    action.action_type = action_data.get('action_type', 'SYSTEM')
                    action.action_parameters = action_data.get('action_parameters', [])
                    action.priority = int(action_data.get('priority', 1))
                    action.timeout.sec = int(action_data.get('timeout', 30.0))
                    action.timeout.nanosec = int((action_data.get('timeout', 30.0) % 1) * 1e9)
                    action.dependencies = action_data.get('dependencies', [])

                    action_sequence.actions.append(action)
                    action_sequence.estimated_duration += action_data.get('timeout', 30.0)

            return action_sequence

        except json.JSONDecodeError as e:
            self.get_logger().error(f'Failed to parse LLM response as JSON: {e}')
            self.get_logger().debug(f'LLM response: {response_text}')
            return None
        except Exception as e:
            self.get_logger().error(f'Error parsing LLM response: {e}')
            return None

    def create_status_message(self, current_state, current_action, progress):
        """Create a VLAStatus message"""
        status_msg = VLAStatus()
        status_msg.current_state = current_state
        status_msg.current_action = current_action
        status_msg.progress_percentage = float(progress)
        status_msg.timestamp = self.get_clock().now().to_msg()
        status_msg.error_message = ""
        status_msg.recent_actions = []  # Will be populated by the integration layer
        return status_msg


def main(args=None):
    rclpy.init(args=args)
    node = CognitivePlannerNode()

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