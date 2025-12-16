#!/usr/bin/env python3
"""
Action Generator Node for VLA System

This node specializes in converting natural language commands to detailed
action sequences, working in conjunction with the cognitive planner.
"""

import rclpy
from rclpy.node import Node
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction
from vla_interfaces.srv import PlanActions
from std_msgs.msg import String
import re
from typing import List, Dict, Any


class ActionGeneratorNode(Node):
    def __init__(self):
        super().__init__('action_generator_node')

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

        # Predefined action templates for common commands
        self.action_templates = {
            'NAVIGATE_TO_LOCATION': self._navigate_to_location,
            'PICK_UP_OBJECT': self._pick_up_object,
            'PLACE_OBJECT': self._place_object,
            'DETECT_OBJECTS': self._detect_objects,
            'CLEAN_ROOM': self._clean_room,
            'FOLLOW_HUMAN': self._follow_human,
            'GENERAL_COMMAND': self._general_command
        }

        self.get_logger().info('Action Generator node initialized')

    def command_callback(self, msg):
        """Callback for VLA command input"""
        self.get_logger().info(f'Received command for action generation: "{msg.command_text}" (intent: {msg.intent})')

        # Generate action sequence based on intent
        action_sequence = self.generate_action_sequence(msg.command_text, msg.intent, msg.parameters)

        if action_sequence:
            # Publish the action sequence
            self.action_sequence_pub.publish(action_sequence)
            self.get_logger().info(f'Published action sequence with {len(action_sequence.actions)} actions')
        else:
            self.get_logger().warn(f'Could not generate action sequence for command: "{msg.command_text}"')

    def plan_actions_callback(self, request, response):
        """Service callback to plan actions from command"""
        try:
            action_sequence = self.generate_action_sequence(
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
                response.error_message = f"Could not generate actions for command: {request.command_text}"
                response.error_code = 2  # Invalid input

        except Exception as e:
            response.success = False
            response.error_message = f"Error in action generation: {e}"
            response.error_code = 1  # General error

        return response

    def generate_action_sequence(self, command_text: str, intent: str, parameters: List[str]) -> VLAActionSequence:
        """Generate an action sequence based on command, intent, and parameters"""
        try:
            # Use the appropriate template based on intent
            if intent in self.action_templates:
                action_sequence = self.action_templates[intent](command_text, parameters)
            else:
                # Default to general command handler
                action_sequence = self._general_command(command_text, parameters)

            # Set additional metadata
            action_sequence.status = 'PENDING'
            action_sequence.safety_level = 'NORMAL'  # Will be validated separately

            # Calculate estimated duration
            total_duration = 0.0
            for action in action_sequence.actions:
                total_duration += action.timeout.sec + (action.timeout.nanosec / 1e9)
            action_sequence.estimated_duration.sec = int(total_duration)
            action_sequence.estimated_duration.nanosec = int((total_duration % 1) * 1e9)

            return action_sequence

        except Exception as e:
            self.get_logger().error(f'Error generating action sequence: {e}')
            return None

    def _navigate_to_location(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for navigation commands"""
        sequence = VLAActionSequence()

        # Extract location from parameters or command
        location = None
        for param in parameters:
            if param.lower() in ['kitchen', 'bedroom', 'living room', 'dining room', 'bathroom', 'office', 'table', 'chair']:
                location = param.lower().replace(' ', '_')  # ROS-friendly format
                break

        if not location:
            # Try to extract from command text
            location = self._extract_location_from_text(command_text)

        if location:
            # Create navigation action
            nav_action = VLAAction()
            nav_action.action_type = 'NAVIGATION'
            nav_action.action_parameters = [f'location={location}']
            nav_action.priority = 1
            nav_action.timeout.sec = 60  # 60 seconds for navigation
            nav_action.timeout.nanosec = 0
            nav_action.dependencies = []

            sequence.actions.append(nav_action)
        else:
            self.get_logger().warn(f'Could not extract location from command: "{command_text}"')

        return sequence

    def _pick_up_object(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for object pickup commands"""
        sequence = VLAActionSequence()

        # Extract object from parameters or command
        obj = None
        color = None

        # Look for object in parameters
        for param in parameters:
            if param.lower() in ['cup', 'bottle', 'book', 'ball', 'box']:
                obj = param.lower()
                break

        # Look for color in parameters
        for param in parameters:
            if param.lower() in ['red', 'blue', 'green', 'yellow', 'black', 'white']:
                color = param.lower()
                break

        # If not found in parameters, extract from command text
        if not obj:
            obj = self._extract_object_from_text(command_text)
        if not color:
            color = self._extract_color_from_text(command_text)

        # Create sequence: detect object -> navigate to object -> grasp object
        if obj:
            # Perception: detect object
            detect_action = VLAAction()
            detect_action.action_type = 'PERCEPTION'
            detect_action.action_parameters = [f'object_type={color + " " + obj if color else obj}']
            detect_action.priority = 1
            detect_action.timeout.sec = 10
            detect_action.timeout.nanosec = 0
            detect_action.dependencies = []
            sequence.actions.append(detect_action)

            # Navigation: go to object
            nav_action = VLAAction()
            nav_action.action_type = 'NAVIGATION'
            nav_action.action_parameters = [f'object_type={color + " " + obj if color else obj}']
            nav_action.priority = 1
            nav_action.timeout.sec = 30
            nav_action.timeout.nanosec = 0
            nav_action.dependencies = [f'PERCEPTION:{detect_action.action_parameters[0]}']
            sequence.actions.append(nav_action)

            # Manipulation: grasp object
            grasp_action = VLAAction()
            grasp_action.action_type = 'MANIPULATION'
            grasp_action.action_parameters = [f'object_type={color + " " + obj if color else obj}']
            grasp_action.priority = 2
            grasp_action.timeout.sec = 15
            grasp_action.timeout.nanosec = 0
            grasp_action.dependencies = [f'NAVIGATION:{nav_action.action_parameters[0]}']
            sequence.actions.append(grasp_action)
        else:
            self.get_logger().warn(f'Could not extract object from command: "{command_text}"')

        return sequence

    def _place_object(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for object placement commands"""
        sequence = VLAActionSequence()

        # Extract location and object
        location = None
        obj = None

        # Extract from parameters
        for param in parameters:
            if param.lower() in ['kitchen', 'table', 'shelf', 'cabinet']:
                location = param.lower()
            elif param.lower() in ['cup', 'bottle', 'book', 'ball', 'box']:
                obj = param.lower()

        # Extract from command text if not found in parameters
        if not location:
            location = self._extract_location_from_text(command_text)
        if not obj:
            obj = self._extract_object_from_text(command_text)

        # Create sequence: navigate to location -> place object
        if location and obj:
            # Navigation: go to location
            nav_action = VLAAction()
            nav_action.action_type = 'NAVIGATION'
            nav_action.action_parameters = [f'location={location}']
            nav_action.priority = 1
            nav_action.timeout.sec = 30
            nav_action.timeout.nanosec = 0
            nav_action.dependencies = []
            sequence.actions.append(nav_action)

            # Manipulation: place object
            place_action = VLAAction()
            place_action.action_type = 'MANIPULATION'
            place_action.action_parameters = [f'object_type={obj}', f'location={location}']
            place_action.priority = 2
            place_action.timeout.sec = 15
            place_action.timeout.nanosec = 0
            place_action.dependencies = [f'NAVIGATION:{nav_action.action_parameters[0]}']
            sequence.actions.append(place_action)
        else:
            self.get_logger().warn(f'Could not extract location and object from command: "{command_text}"')

        return sequence

    def _detect_objects(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for object detection commands"""
        sequence = VLAActionSequence()

        # Extract object types to detect
        object_types = []
        for param in parameters:
            if param.lower() in ['cup', 'bottle', 'book', 'ball', 'box', 'red', 'blue', 'green']:
                object_types.append(param.lower())

        # If not found in parameters, extract from command text
        if not object_types:
            object_types = self._extract_objects_from_text(command_text)

        if object_types:
            detect_action = VLAAction()
            detect_action.action_type = 'PERCEPTION'
            detect_action.action_parameters = [f'object_types={object_types}']
            detect_action.priority = 1
            detect_action.timeout.sec = 20
            detect_action.timeout.nanosec = 0
            detect_action.dependencies = []
            sequence.actions.append(detect_action)
        else:
            # If no specific objects mentioned, detect all common objects
            detect_action = VLAAction()
            detect_action.action_type = 'PERCEPTION'
            detect_action.action_parameters = ['object_types=["cup", "bottle", "book", "ball", "box"]']
            detect_action.priority = 1
            detect_action.timeout.sec = 20
            detect_action.timeout.nanosec = 0
            detect_action.dependencies = []
            sequence.actions.append(detect_action)

        return sequence

    def _clean_room(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for room cleaning commands"""
        sequence = VLAActionSequence()

        # Create a complex sequence for cleaning: detect objects -> pick up -> place appropriately
        # This is a simplified version; in reality, this would be more sophisticated

        # Perception: detect objects that need to be organized
        detect_action = VLAAction()
        detect_action.action_type = 'PERCEPTION'
        detect_action.action_parameters = ['object_types=["cup", "bottle", "book", "ball", "box"]']
        detect_action.priority = 1
        detect_action.timeout.sec = 30
        detect_action.timeout.nanosec = 0
        detect_action.dependencies = []
        sequence.actions.append(detect_action)

        # Navigation: go to first detected object
        nav_action = VLAAction()
        nav_action.action_type = 'NAVIGATION'
        nav_action.action_parameters = ['object_type=any_scattered_object']
        nav_action.priority = 1
        nav_action.timeout.sec = 30
        nav_action.timeout.nanosec = 0
        nav_action.dependencies = [f'PERCEPTION:{detect_action.action_parameters[0]}']
        sequence.actions.append(nav_action)

        # Manipulation: pick up object
        grasp_action = VLAAction()
        grasp_action.action_type = 'MANIPULATION'
        grasp_action.action_parameters = ['object_type=detected_object']
        grasp_action.priority = 2
        grasp_action.timeout.sec = 15
        grasp_action.timeout.nanosec = 0
        grasp_action.dependencies = [f'NAVIGATION:{nav_action.action_parameters[0]}']
        sequence.actions.append(grasp_action)

        # Navigation: go to appropriate storage location
        storage_nav_action = VLAAction()
        storage_nav_action.action_type = 'NAVIGATION'
        storage_nav_action.action_parameters = ['location=storage_area']
        storage_nav_action.priority = 1
        storage_nav_action.timeout.sec = 30
        storage_nav_action.timeout.nanosec = 0
        storage_nav_action.dependencies = [f'MANIPULATION:{grasp_action.action_parameters[0]}']
        sequence.actions.append(storage_nav_action)

        # Manipulation: place object
        place_action = VLAAction()
        place_action.action_type = 'MANIPULATION'
        place_action.action_parameters = ['object_type=held_object', 'location=storage_area']
        place_action.priority = 2
        place_action.timeout.sec = 15
        place_action.timeout.nanosec = 0
        place_action.dependencies = [f'NAVIGATION:{storage_nav_action.action_parameters[0]}']
        sequence.actions.append(place_action)

        # System: wait briefly before continuing
        wait_action = VLAAction()
        wait_action.action_type = 'SYSTEM'
        wait_action.action_parameters = ['duration=2.0']
        wait_action.priority = 0
        wait_action.timeout.sec = 5
        wait_action.timeout.nanosec = 0
        wait_action.dependencies = [f'MANIPULATION:{place_action.action_parameters[0]}']
        sequence.actions.append(wait_action)

        return sequence

    def _follow_human(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for following a human"""
        sequence = VLAActionSequence()

        # Perception: detect human
        detect_action = VLAAction()
        detect_action.action_type = 'PERCEPTION'
        detect_action.action_parameters = ['object_type=human']
        detect_action.priority = 2
        detect_action.timeout.sec = 10
        detect_action.timeout.nanosec = 0
        detect_action.dependencies = []
        sequence.actions.append(detect_action)

        # Navigation: follow human
        follow_action = VLAAction()
        follow_action.action_type = 'NAVIGATION'
        follow_action.action_parameters = ['object_type=human', 'follow_mode=true']
        follow_action.priority = 2
        follow_action.timeout.sec = 300  # 5 minutes for following
        follow_action.timeout.nanosec = 0
        follow_action.dependencies = [f'PERCEPTION:{detect_action.action_parameters[0]}']
        sequence.actions.append(follow_action)

        return sequence

    def _general_command(self, command_text: str, parameters: List[str]) -> VLAActionSequence:
        """Generate actions for general commands"""
        sequence = VLAActionSequence()

        # For general commands, we'll try to infer the intent and create appropriate actions
        command_lower = command_text.lower()

        # Simple intent inference
        if any(word in command_lower for word in ['hello', 'hi', 'greet', 'hey']):
            # Speak action
            speak_action = VLAAction()
            speak_action.action_type = 'SYSTEM'
            speak_action.action_parameters = ['text=Hello! How can I assist you?']
            speak_action.priority = 1
            speak_action.timeout.sec = 10
            speak_action.timeout.nanosec = 0
            speak_action.dependencies = []
            sequence.actions.append(speak_action)
        elif any(word in command_lower for word in ['stop', 'halt', 'pause']):
            # Stop action (could be implemented as emergency stop)
            stop_action = VLAAction()
            stop_action.action_type = 'SYSTEM'
            stop_action.action_parameters = ['command=stop_all_actions']
            stop_action.priority = 2
            stop_action.timeout.sec = 5
            stop_action.timeout.nanosec = 0
            stop_action.dependencies = []
            sequence.actions.append(stop_action)
        else:
            # For unrecognized commands, ask for clarification
            ask_action = VLAAction()
            ask_action.action_type = 'SYSTEM'
            ask_action.action_parameters = [f'text=I\'m not sure how to perform: {command_text}. Could you clarify?']
            ask_action.priority = 1
            ask_action.timeout.sec = 10
            ask_action.timeout.nanosec = 0
            ask_action.dependencies = []
            sequence.actions.append(ask_action)

        return sequence

    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from command text using pattern matching"""
        text_lower = text.lower()

        # Common locations
        locations = {
            'kitchen': ['kitchen'],
            'bedroom': ['bedroom'],
            'living room': ['living room', 'livingroom'],
            'dining room': ['dining room', 'dining'],
            'bathroom': ['bathroom', 'bath'],
            'office': ['office'],
            'table': ['table'],
            'chair': ['chair'],
            'couch': ['couch', 'sofa']
        }

        for location, keywords in locations.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return location.replace(' ', '_')

        return None

    def _extract_object_from_text(self, text: str) -> str:
        """Extract object from command text using pattern matching"""
        text_lower = text.lower()

        # Common objects
        objects = ['cup', 'bottle', 'book', 'ball', 'box', 'plate', 'fork', 'spoon', 'glass', 'phone']

        for obj in objects:
            if obj in text_lower:
                return obj

        return None

    def _extract_color_from_text(self, text: str) -> str:
        """Extract color from command text"""
        text_lower = text.lower()

        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'orange', 'purple', 'pink', 'brown']

        for color in colors:
            if color in text_lower:
                return color

        return None

    def _extract_objects_from_text(self, text: str) -> List[str]:
        """Extract multiple objects from command text"""
        text_lower = text.lower()

        objects = ['cup', 'bottle', 'book', 'ball', 'box', 'plate', 'fork', 'spoon', 'glass', 'phone']
        found_objects = []

        for obj in objects:
            if obj in text_lower:
                found_objects.append(obj)

        return found_objects


def main(args=None):
    rclpy.init(args=args)
    node = ActionGeneratorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()