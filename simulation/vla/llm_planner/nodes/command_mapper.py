#!/usr/bin/env python3
"""
Command Mapper Node for VLA System

This node maps natural language commands to appropriate action sequences
using rule-based and semantic matching approaches.
"""

import rclpy
from rclpy.node import Node
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction
from vla_interfaces.srv import PlanActions
from std_msgs.msg import String
import re
from typing import List, Dict, Any, Tuple
from enum import Enum


class CommandCategory(Enum):
    """Categories of commands supported by the system"""
    NAVIGATION = "NAVIGATION"
    MANIPULATION = "MANIPULATION"
    PERCEPTION = "PERCEPTION"
    SYSTEM = "SYSTEM"
    GENERAL = "GENERAL"


class CommandMapperNode(Node):
    def __init__(self):
        super().__init__('command_mapper_node')

        # Declare parameters
        self.declare_parameter('enable_context_awareness', True)
        self.declare_parameter('enable_safety_validation', True)
        self.declare_parameter('enable_multi_step_planning', True)
        self.declare_parameter('input_command_topic', '/vla/command')
        self.declare_parameter('output_action_sequence_topic', '/vla/action_sequence')
        self.declare_parameter('plan_actions_service', '/vla/plan_actions')
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')

        # Get parameters
        self.enable_context_awareness = self.get_parameter('enable_context_awareness').value
        self.enable_safety_validation = self.get_parameter('enable_safety_validation').value
        self.enable_multi_step_planning = self.get_parameter('enable_multi_step_planning').value
        input_command_topic = self.get_parameter('input_command_topic').value
        output_action_sequence_topic = self.get_parameter('output_action_sequence_topic').value
        plan_actions_service = self.get_parameter('plan_actions_service').value
        self.enable_debug = self.get_parameter('enable_debug').value

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

        # Create service server
        self.plan_actions_srv = self.create_service(
            PlanActions,
            plan_actions_service,
            self.plan_actions_callback
        )

        # Initialize command mapping patterns
        self._initialize_command_patterns()

        self.get_logger().info('Command Mapper node initialized')

    def _initialize_command_patterns(self):
        """Initialize patterns for command categorization and parameter extraction"""
        self.navigation_patterns = [
            (r'go\s+to\s+(the\s+)?(\w+)', CommandCategory.NAVIGATION),
            (r'move\s+to\s+(the\s+)?(\w+)', CommandCategory.NAVIGATION),
            (r'navigate\s+to\s+(the\s+)?(\w+)', CommandCategory.NAVIGATION),
            (r'walk\s+to\s+(the\s+)?(\w+)', CommandCategory.NAVIGATION),
            (r'run\s+to\s+(the\s+)?(\w+)', CommandCategory.NAVIGATION),
            (r'travel\s+to\s+(the\s+)?(\w+)', CommandCategory.NAVIGATION),
        ]

        self.manipulation_patterns = [
            (r'pick\s+up\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'grasp\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'take\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'grab\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'lift\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'hold\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'get\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'put\s+(down|away|back)\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'place\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'set\s+(down|back)\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'release\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
            (r'drop\s+(the\s+)?(\w+)', CommandCategory.MANIPULATION),
        ]

        self.perception_patterns = [
            (r'find\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'locate\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'look\s+for\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'search\s+for\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'detect\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'see\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'spot\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
            (r'identify\s+(the\s+)?(\w+)', CommandCategory.PERCEPTION),
        ]

        self.system_patterns = [
            (r'hello|hi|hey|greet', CommandCategory.SYSTEM),
            (r'stop|halt|pause|freeze', CommandCategory.SYSTEM),
            (r'resume|continue|start', CommandCategory.SYSTEM),
            (r'help|assist|support', CommandCategory.SYSTEM),
            (r'wait|hold|standby', CommandCategory.SYSTEM),
        ]

        # Object extraction patterns
        self.object_patterns = [
            r'(\w+)\s+cups?',
            r'(\w+)\s+bottles?',
            r'(\w+)\s+books?',
            r'(\w+)\s+balls?',
            r'(\w+)\s+boxes?',
            r'(\w+)\s+plates?',
            r'(\w+)\s+forks?',
            r'(\w+)\s+spoons?',
            r'(\w+)\s+glasses?',
            r'(\w+)\s+phones?',
            r'(red|blue|green|yellow|black|white|orange|purple|pink|brown)\s+(\w+)',
        ]

        # Location extraction patterns
        self.location_patterns = [
            r'kitchen|bedroom|living room|dining room|bathroom|office|table|chair|couch|sofa|desk'
        ]

    def command_callback(self, msg):
        """Callback for VLA command input"""
        self.get_logger().info(f'Received command for mapping: "{msg.command_text}" (confidence: {msg.confidence_score:.2f})')

        # Map command to action sequence
        action_sequence = self.map_command_to_actions(msg.command_text, msg.intent, msg.parameters)

        if action_sequence:
            # Publish the action sequence
            self.action_sequence_pub.publish(action_sequence)
            self.get_logger().info(f'Published mapped action sequence with {len(action_sequence.actions)} actions')
        else:
            self.get_logger().warn(f'Could not map command to actions: "{msg.command_text}"')

    def plan_actions_callback(self, request, response):
        """Service callback to plan actions from command"""
        try:
            action_sequence = self.map_command_to_actions(
                request.command_text,
                request.intent,
                request.parameters
            )

            if action_sequence:
                response.success = True
                response.action_sequence = action_sequence
                response.error_message = ""
                response.error_code = 0
            else:
                response.success = False
                response.error_message = f"Could not map command to actions: {request.command_text}"
                response.error_code = 2  # Invalid input

        except Exception as e:
            response.success = False
            response.error_message = f"Error in command mapping: {e}"
            response.error_code = 1  # General error

        return response

    def map_command_to_actions(self, command_text: str, intent: str, parameters: List[str]) -> VLAActionSequence:
        """Map a natural language command to an action sequence"""
        try:
            # If intent is already provided, use it directly
            if intent and intent != 'GENERAL_COMMAND':
                command_category = CommandCategory(intent)
            else:
                # Otherwise, categorize the command
                command_category, extracted_params = self.categorize_command(command_text)

            # Generate appropriate action sequence based on category
            if command_category == CommandCategory.NAVIGATION:
                action_sequence = self._create_navigation_sequence(command_text, parameters)
            elif command_category == CommandCategory.MANIPULATION:
                action_sequence = self._create_manipulation_sequence(command_text, parameters)
            elif command_category == CommandCategory.PERCEPTION:
                action_sequence = self._create_perception_sequence(command_text, parameters)
            elif command_category == CommandCategory.SYSTEM:
                action_sequence = self._create_system_sequence(command_text, parameters)
            else:
                action_sequence = self._create_general_sequence(command_text, parameters)

            # Set metadata
            action_sequence.status = 'PENDING'
            action_sequence.safety_level = 'NORMAL'

            # Calculate estimated duration
            total_duration = 0.0
            for action in action_sequence.actions:
                total_duration += action.timeout.sec + (action.timeout.nanosec / 1e9)
            action_sequence.estimated_duration.sec = int(total_duration)
            action_sequence.estimated_duration.nanosec = int((total_duration % 1) * 1e9)

            return action_sequence

        except Exception as e:
            self.get_logger().error(f'Error mapping command to actions: {e}')
            return None

    def categorize_command(self, command_text: str) -> Tuple[CommandCategory, List[str]]:
        """Categorize a command and extract parameters"""
        text_lower = command_text.lower()
        extracted_params = []

        # Check navigation patterns
        for pattern, category in self.navigation_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract location parameter
                if len(match.groups()) > 1:
                    extracted_params.append(match.group(2))
                return category, extracted_params

        # Check manipulation patterns
        for pattern, category in self.manipulation_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract object parameter
                if len(match.groups()) > 1:
                    extracted_params.append(match.group(len(match.groups())))  # Get the last group (object)
                return category, extracted_params

        # Check perception patterns
        for pattern, category in self.perception_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract object parameter
                if len(match.groups()) > 1:
                    extracted_params.append(match.group(2))
                return category, extracted_params

        # Check system patterns
        for pattern, category in self.system_patterns:
            if re.search(pattern, text_lower):
                return category, extracted_params

        # If no specific pattern matched, return general
        return CommandCategory.GENERAL, extracted_params

    def _create_navigation_sequence(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Create navigation action sequence"""
        sequence = VLAActionSequence()

        # Extract destination
        destination = None
        if parameters:
            destination = parameters[0].lower().replace(' ', '_')
        else:
            # Try to extract from command text
            for pattern, _ in self.navigation_patterns:
                match = re.search(pattern, command_text.lower())
                if match and len(match.groups()) > 1:
                    destination = match.group(2).lower().replace(' ', '_')
                    break

        if destination:
            nav_action = VLAAction()
            nav_action.action_type = 'NAVIGATION'
            nav_action.action_parameters = [f'location={destination}']
            nav_action.priority = 1
            nav_action.timeout.sec = 60  # 60 seconds for navigation
            nav_action.timeout.nanosec = 0
            nav_action.dependencies = []

            sequence.actions.append(nav_action)
        else:
            self.get_logger().warn(f'Could not extract destination from navigation command: "{command_text}"')

        return sequence

    def _create_manipulation_sequence(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Create manipulation action sequence"""
        sequence = VLAActionSequence()

        # Extract object
        obj = None
        if parameters:
            obj = parameters[0].lower()
        else:
            # Try to extract from command text
            for pattern, _ in self.manipulation_patterns:
                match = re.search(pattern, command_text.lower())
                if match:
                    # Get the last group which should be the object
                    groups = match.groups()
                    if groups:
                        obj = groups[-1].lower()
                    break

        if obj:
            # Create a sequence: detect -> navigate -> manipulate
            # Perception: detect object
            detect_action = VLAAction()
            detect_action.action_type = 'PERCEPTION'
            detect_action.action_parameters = [f'object_type={obj}']
            detect_action.priority = 1
            detect_action.timeout.sec = 10
            detect_action.timeout.nanosec = 0
            detect_action.dependencies = []
            sequence.actions.append(detect_action)

            # Navigation: go to object
            nav_action = VLAAction()
            nav_action.action_type = 'NAVIGATION'
            nav_action.action_parameters = [f'object_type={obj}']
            nav_action.priority = 1
            nav_action.timeout.sec = 30
            nav_action.timeout.nanosec = 0
            nav_action.dependencies = [f'PERCEPTION:{detect_action.action_parameters[0]}']
            sequence.actions.append(nav_action)

            # Manipulation: perform action
            manipulation_action = VLAAction()
            if any(word in command_text.lower() for word in ['pick', 'grasp', 'take', 'grab', 'lift', 'hold', 'get']):
                manipulation_action.action_type = 'MANIPULATION'
                manipulation_action.action_parameters = [f'object_type={obj}', 'action=grasp']
            elif any(word in command_text.lower() for word in ['put', 'place', 'set', 'release', 'drop']):
                manipulation_action.action_type = 'MANIPULATION'
                manipulation_action.action_parameters = [f'object_type={obj}', 'action=place']
            else:
                manipulation_action.action_type = 'MANIPULATION'
                manipulation_action.action_parameters = [f'object_type={obj}']

            manipulation_action.priority = 2
            manipulation_action.timeout.sec = 15
            manipulation_action.timeout.nanosec = 0
            manipulation_action.dependencies = [f'NAVIGATION:{nav_action.action_parameters[0]}']
            sequence.actions.append(manipulation_action)
        else:
            self.get_logger().warn(f'Could not extract object from manipulation command: "{command_text}"')

        return sequence

    def _create_perception_sequence(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Create perception action sequence"""
        sequence = VLAActionSequence()

        # Extract object to detect
        obj = None
        if parameters:
            obj = parameters[0].lower()
        else:
            # Try to extract from command text
            for pattern, _ in self.perception_patterns:
                match = re.search(pattern, command_text.lower())
                if match and len(match.groups()) > 1:
                    obj = match.group(2).lower()
                    break

        if obj:
            detect_action = VLAAction()
            detect_action.action_type = 'PERCEPTION'
            detect_action.action_parameters = [f'object_type={obj}']
            detect_action.priority = 1
            detect_action.timeout.sec = 20
            detect_action.timeout.nanosec = 0
            detect_action.dependencies = []
            sequence.actions.append(detect_action)
        else:
            # If no specific object, detect common objects
            detect_action = VLAAction()
            detect_action.action_type = 'PERCEPTION'
            detect_action.action_parameters = ['object_types=["cup", "bottle", "book", "ball", "box"]']
            detect_action.priority = 1
            detect_action.timeout.sec = 20
            detect_action.timeout.nanosec = 0
            detect_action.dependencies = []
            sequence.actions.append(detect_action)

        return sequence

    def _create_system_sequence(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Create system action sequence"""
        sequence = VLAActionSequence()

        text_lower = command_text.lower()

        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greet']):
            speak_action = VLAAction()
            speak_action.action_type = 'SYSTEM'
            speak_action.action_parameters = ['text=Hello! How can I assist you?']
            speak_action.priority = 1
            speak_action.timeout.sec = 10
            speak_action.timeout.nanosec = 0
            speak_action.dependencies = []
            sequence.actions.append(speak_action)
        elif any(word in text_lower for word in ['stop', 'halt', 'pause', 'freeze']):
            stop_action = VLAAction()
            stop_action.action_type = 'SYSTEM'
            stop_action.action_parameters = ['command=stop_all_actions']
            stop_action.priority = 2
            stop_action.timeout.sec = 5
            stop_action.timeout.nanosec = 0
            stop_action.dependencies = []
            sequence.actions.append(stop_action)
        elif any(word in text_lower for word in ['resume', 'continue', 'start']):
            resume_action = VLAAction()
            resume_action.action_type = 'SYSTEM'
            resume_action.action_parameters = ['command=resume_actions']
            resume_action.priority = 1
            resume_action.timeout.sec = 5
            resume_action.timeout.nanosec = 0
            resume_action.dependencies = []
            sequence.actions.append(resume_action)
        elif any(word in text_lower for word in ['wait', 'hold', 'standby']):
            wait_action = VLAAction()
            wait_action.action_type = 'SYSTEM'
            wait_action.action_parameters = ['duration=5.0']
            wait_action.priority = 0
            wait_action.timeout.sec = 10
            wait_action.timeout.nanosec = 0
            wait_action.dependencies = []
            sequence.actions.append(wait_action)
        else:
            # Default system response
            default_action = VLAAction()
            default_action.action_type = 'SYSTEM'
            default_action.action_parameters = [f'text=Understood: {command_text}']
            default_action.priority = 1
            default_action.timeout.sec = 5
            default_action.timeout.nanosec = 0
            default_action.dependencies = []
            sequence.actions.append(default_action)

        return sequence

    def _create_general_sequence(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Create general action sequence for unrecognized commands"""
        sequence = VLAActionSequence()

        # For general commands, try to infer intent based on keywords
        text_lower = command_text.lower()

        # Try to infer intent based on keywords
        if any(word in text_lower for word in ['go', 'move', 'navigate', 'walk', 'run', 'travel']):
            # Likely a navigation command
            return self._create_navigation_sequence(command_text, parameters)
        elif any(word in text_lower for word in ['pick', 'grasp', 'take', 'grab', 'lift', 'hold', 'get', 'put', 'place', 'set', 'release', 'drop']):
            # Likely a manipulation command
            return self._create_manipulation_sequence(command_text, parameters)
        elif any(word in text_lower for word in ['find', 'locate', 'look', 'search', 'detect', 'see', 'spot', 'identify']):
            # Likely a perception command
            return self._create_perception_sequence(command_text, parameters)
        else:
            # Ask for clarification
            ask_action = VLAAction()
            ask_action.action_type = 'SYSTEM'
            ask_action.action_parameters = [f'text=I\'m not sure how to perform: {command_text}. Could you clarify?']
            ask_action.priority = 1
            ask_action.timeout.sec = 10
            ask_action.timeout.nanosec = 0
            ask_action.dependencies = []
            sequence.actions.append(ask_action)

        return sequence


def main(args=None):
    rclpy.init(args=args)
    node = CommandMapperNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()