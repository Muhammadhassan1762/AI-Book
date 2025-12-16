#!/usr/bin/env python3
"""
Safety Validator Node for VLA System

This node validates the safety of action sequences before execution,
checking for potential hazards and ensuring safe robot behavior.
"""

import rclpy
from rclpy.node import Node
from vla_interfaces.msg import VLAActionSequence, VLAAction, VLAStatus
from vla_interfaces.srv import ValidateSafety, ProcessCommand
from std_msgs.msg import String
from typing import List, Tuple, Dict, Any
import math


class SafetyValidatorNode(Node):
    def __init__(self):
        super().__init__('safety_validator_node')

        # Declare parameters
        self.declare_parameter('enable_safety_validation', True)
        self.declare_parameter('safety_threshold', 0.8)
        self.declare_parameter('check_navigation_safety', True)
        self.declare_parameter('check_manipulation_safety', True)
        self.declare_parameter('check_perception_safety', True)
        self.declare_parameter('check_system_safety', True)
        self.declare_parameter('min_navigation_distance', 0.1)  # meters
        self.declare_parameter('max_navigation_distance', 100.0)  # meters
        self.declare_parameter('max_manipulation_force', 50.0)  # Newtons
        self.declare_parameter('max_velocity', 1.0)  # m/s
        self.declare_parameter('validate_safety_service', '/vla/validate_safety')
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')

        # Get parameters
        self.enable_safety_validation = self.get_parameter('enable_safety_validation').value
        self.safety_threshold = self.get_parameter('safety_threshold').value
        self.check_navigation_safety = self.get_parameter('check_navigation_safety').value
        self.check_manipulation_safety = self.get_parameter('check_manipulation_safety').value
        self.check_perception_safety = self.get_parameter('check_perception_safety').value
        self.check_system_safety = self.get_parameter('check_system_safety').value
        self.min_navigation_distance = self.get_parameter('min_navigation_distance').value
        self.max_navigation_distance = self.get_parameter('max_navigation_distance').value
        self.max_manipulation_force = self.get_parameter('max_manipulation_force').value
        self.max_velocity = self.get_parameter('max_velocity').value
        validate_safety_service = self.get_parameter('validate_safety_service').value
        self.enable_debug = self.get_parameter('enable_debug').value

        # Create service server
        self.validate_safety_srv = self.create_service(
            ValidateSafety,
            validate_safety_service,
            self.validate_safety_callback
        )

        # Initialize safety database (in a real system, this would be more sophisticated)
        self.known_safe_locations = set(['kitchen', 'living_room', 'bedroom', 'office'])
        self.known_safe_objects = set(['cup', 'bottle', 'book', 'ball', 'box'])
        self.known_hazardous_objects = set(['knife', 'scissors', 'hot_item'])

        self.get_logger().info('Safety Validator node initialized')

    def validate_safety_callback(self, request, response):
        """Service callback to validate safety of action sequence"""
        if not self.enable_safety_validation:
            self.get_logger().info('Safety validation disabled, approving sequence')
            response.is_safe = True
            response.requires_confirmation = False
            response.safety_issues = []
            response.error_message = ""
            response.error_code = 0
            return response

        try:
            is_safe, requires_confirmation, issues = self.validate_action_sequence(request.action_sequence)

            response.is_safe = is_safe
            response.requires_confirmation = requires_confirmation
            response.safety_issues = issues
            response.error_message = ""
            response.error_code = 0

            if is_safe:
                self.get_logger().info(f'Safety validation passed: {len(issues)} issues found (all minor)')
            else:
                self.get_logger().warn(f'Safety validation failed: {len(issues)} critical issues found')

        except Exception as e:
            self.get_logger().error(f'Safety validation error: {e}')
            response.is_safe = False
            response.requires_confirmation = False
            response.safety_issues = [f'Safety validation error: {e}']
            response.error_message = f'Safety validation error: {e}'
            response.error_code = 1

        return response

    def validate_action_sequence(self, action_sequence: VLAActionSequence) -> Tuple[bool, bool, List[str]]:
        """
        Validate the safety of an entire action sequence
        Returns: (is_safe, requires_confirmation, safety_issues)
        """
        all_issues = []
        critical_issues = []

        for i, action in enumerate(action_sequence.actions):
            action_issues = self.validate_single_action(action, i)
            all_issues.extend(action_issues)

            # Check for critical issues
            for issue in action_issues:
                if any(keyword in issue.lower() for keyword in ['collision', 'hazardous', 'unsafe', 'dangerous']):
                    critical_issues.append(issue)

        # Determine if the sequence is safe
        is_safe = len(critical_issues) == 0
        requires_confirmation = len(all_issues) > 0 and len(critical_issues) == 0

        return is_safe, requires_confirmation, all_issues

    def validate_single_action(self, action: VLAAction, action_index: int) -> List[str]:
        """Validate the safety of a single action"""
        issues = []

        if action.action_type == 'NAVIGATION':
            issues.extend(self.validate_navigation_action(action, action_index))
        elif action.action_type == 'MANIPULATION':
            issues.extend(self.validate_manipulation_action(action, action_index))
        elif action.action_type == 'PERCEPTION':
            issues.extend(self.validate_perception_action(action, action_index))
        elif action.action_type == 'SYSTEM':
            issues.extend(self.validate_system_action(action, action_index))
        else:
            issues.append(f'Unknown action type at index {action_index}: {action.action_type}')

        return issues

    def validate_navigation_action(self, action: VLAAction, action_index: int) -> List[str]:
        """Validate navigation action safety"""
        if not self.check_navigation_safety:
            return []

        issues = []

        # Parse parameters
        target_location = None
        target_object = None
        approach_distance = None

        for param in action.action_parameters:
            if param.startswith('location='):
                target_location = param.split('=', 1)[1].lower()
            elif param.startswith('object_id=') or param.startswith('object_type='):
                target_object = param.split('=', 1)[1].lower()
            elif param.startswith('approach_distance='):
                try:
                    approach_distance = float(param.split('=', 1)[1])
                except ValueError:
                    issues.append(f'Invalid approach distance in navigation action {action_index}')

        # Check if target location is known and safe
        if target_location:
            if target_location not in self.known_safe_locations:
                issues.append(f'Unknown or unsafe navigation target at index {action_index}: {target_location}')

        # Check approach distance
        if approach_distance is not None:
            if approach_distance < self.min_navigation_distance:
                issues.append(f'Approach distance too close in navigation action {action_index}: {approach_distance}m < {self.min_navigation_distance}m')
            elif approach_distance > self.max_navigation_distance:
                issues.append(f'Approach distance too far in navigation action {action_index}: {approach_distance}m > {self.max_navigation_distance}m')

        # Check for potential collisions based on action timeout (duration)
        if action.timeout.sec > 300:  # 5 minutes
            issues.append(f'Navigation action {action_index} has excessive timeout: {action.timeout.sec}s')

        return issues

    def validate_manipulation_action(self, action: VLAAction, action_index: int) -> List[str]:
        """Validate manipulation action safety"""
        if not self.check_manipulation_safety:
            return []

        issues = []

        # Parse parameters
        target_object = None
        grasp_type = None
        force_limit = None

        for param in action.action_parameters:
            if param.startswith('object_id=') or param.startswith('object_type='):
                target_object = param.split('=', 1)[1].lower()
            elif param.startswith('grasp_type='):
                grasp_type = param.split('=', 1)[1].lower()
            elif param.startswith('force_limit='):
                try:
                    force_limit = float(param.split('=', 1)[1])
                except ValueError:
                    issues.append(f'Invalid force limit in manipulation action {action_index}')

        # Check if object is hazardous
        if target_object:
            if target_object in self.known_hazardous_objects:
                issues.append(f'Hazardous object in manipulation action {action_index}: {target_object}')
            elif target_object not in self.known_safe_objects:
                issues.append(f'Unknown object in manipulation action {action_index}: {target_object}')

        # Check force limits
        if force_limit and force_limit > self.max_manipulation_force:
            issues.append(f'Force limit exceeds maximum in manipulation action {action_index}: {force_limit}N > {self.max_manipulation_force}N')

        # Check timeout for manipulation (shouldn't be too long)
        if action.timeout.sec > 60:  # 1 minute
            issues.append(f'Manipulation action {action_index} has excessive timeout: {action.timeout.sec}s')

        return issues

    def validate_perception_action(self, action: VLAAction, action_index: int) -> List[str]:
        """Validate perception action safety"""
        if not self.check_perception_safety:
            return []

        issues = []

        # Parse parameters
        object_types = []
        detection_range = None

        for param in action.action_parameters:
            if param.startswith('object_types='):
                # Extract object types from the parameter (simplified parsing)
                try:
                    # This is a simplified parsing - in a real system, you'd want proper JSON parsing
                    types_str = param.split('=', 1)[1]
                    # Remove brackets and quotes for simple parsing
                    types_str = types_str.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
                    object_types = [t.strip() for t in types_str.split(',')]
                except:
                    issues.append(f'Invalid object types format in perception action {action_index}')
            elif param.startswith('detection_range='):
                try:
                    detection_range = float(param.split('=', 1)[1])
                except ValueError:
                    issues.append(f'Invalid detection range in perception action {action_index}')

        # Check detection range
        if detection_range and detection_range > 10.0:  # 10 meters max range
            issues.append(f'Detection range too large in perception action {action_index}: {detection_range}m > 10.0m')

        # Check for hazardous object detection requests
        for obj_type in object_types:
            if obj_type in self.known_hazardous_objects:
                issues.append(f'Request to detect hazardous object in perception action {action_index}: {obj_type}')

        return issues

    def validate_system_action(self, action: VLAAction, action_index: int) -> List[str]:
        """Validate system action safety"""
        if not self.check_system_safety:
            return []

        issues = []

        # Parse parameters
        duration = None
        text = None
        command = None

        for param in action.action_parameters:
            if param.startswith('duration='):
                try:
                    duration = float(param.split('=', 1)[1])
                except ValueError:
                    issues.append(f'Invalid duration in system action {action_index}')
            elif param.startswith('text='):
                text = param.split('=', 1)[1]
            elif param.startswith('command='):
                command = param.split('=', 1)[1]

        # Check duration
        if duration and duration > 300:  # 5 minutes max wait
            issues.append(f'Duration too long in system action {action_index}: {duration}s > 300s')

        # Check for unsafe commands
        if command:
            unsafe_commands = ['shutdown', 'power_off', 'emergency_stop']
            if any(unsafe_cmd in command.lower() for unsafe_cmd in unsafe_commands):
                issues.append(f'Potentially unsafe command in system action {action_index}: {command}')

        # Check for inappropriate text (in a real system, you'd have more sophisticated content filtering)
        if text:
            # Simple check for potentially inappropriate content
            inappropriate_keywords = ['shut down', 'power off', 'stop immediately']
            if any(keyword in text.lower() for keyword in inappropriate_keywords):
                issues.append(f'Potentially inappropriate text in system action {action_index}: {text}')

        return issues

    def check_environment_safety(self, location: str) -> bool:
        """Check if environment is safe for operation"""
        # In a real system, this would check sensor data, maps, etc.
        # For simulation, we'll assume known locations are safe
        return location in self.known_safe_locations

    def check_object_safety(self, obj_type: str) -> Tuple[bool, str]:
        """Check if object is safe to interact with"""
        if obj_type in self.known_hazardous_objects:
            return False, f'Hazardous object: {obj_type}'
        elif obj_type in self.known_safe_objects:
            return True, ''
        else:
            return False, f'Unknown object type: {obj_type} (safety unknown)'

    def check_path_safety(self, start_location: str, end_location: str) -> Tuple[bool, List[str]]:
        """Check if path between locations is safe"""
        # In a real system, this would check navigation maps, obstacles, etc.
        # For simulation, we'll assume paths between known safe locations are safe
        if start_location in self.known_safe_locations and end_location in self.known_safe_locations:
            return True, []
        else:
            return False, [f'Path from {start_location} to {end_location} may not be safe']


def main(args=None):
    rclpy.init(args=args)
    node = SafetyValidatorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()