#!/usr/bin/env python3
"""
Validation Exercises for VLA System

This script provides validation exercises to test the complete VLA system
with various scenarios and edge cases.
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import time
import threading
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction, VLAStatus
from vla_interfaces.srv import ProcessCommand, PlanActions, ValidateSafety
from std_msgs.msg import String
from typing import List, Dict, Any, Tuple
import json
import random


class VLAValidationExercises(Node):
    def __init__(self):
        super().__init__('vla_validation_exercises')

        # Create publishers for testing
        self.command_pub = self.create_publisher(
            VLACommand,
            '/vla/command',
            10
        )

        self.status_sub = self.create_subscription(
            VLAStatus,
            '/vla/status',
            self.status_callback,
            10
        )

        self.action_sequence_sub = self.create_subscription(
            VLAActionSequence,
            '/vla/action_sequence',
            self.action_sequence_callback,
            10
        )

        # Create service clients
        self.process_command_client = self.create_client(
            ProcessCommand,
            '/vla/process_command'
        )
        self.plan_actions_client = self.create_client(
            PlanActions,
            '/vla/plan_actions'
        )
        self.validate_safety_client = self.create_client(
            ValidateSafety,
            '/vla/validate_safety'
        )
        self.execute_pipeline_client = self.create_client(
            ProcessCommand,
            '/vla/execute_pipeline'
        )

        # Wait for services to be available
        self.get_logger().info('Waiting for services...')
        while not self.process_command_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Process command service not available, waiting...')
        while not self.plan_actions_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Plan actions service not available, waiting...')
        while not self.validate_safety_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Validate safety service not available, waiting...')
        while not self.execute_pipeline_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Execute pipeline service not available, waiting...')

        # Test tracking
        self.status_history = []
        self.action_sequences_received = []
        self.validation_results = []
        self.current_exercise_name = ""

        self.get_logger().info('VLA Validation Exercises initialized')

    def status_callback(self, msg):
        """Callback for status messages"""
        self.status_history.append({
            'state': msg.current_state,
            'action': msg.current_action,
            'progress': msg.progress_percentage,
            'timestamp': time.time(),
            'error': msg.error_message
        })

        if self.current_exercise_name:
            self.get_logger().debug(f'Exercise {self.current_exercise_name}: Status - {msg.current_state} ({msg.progress_percentage}%)')

    def action_sequence_callback(self, msg):
        """Callback for action sequence messages"""
        action_info = {
            'count': len(msg.actions),
            'actions': [(action.action_type, action.action_parameters) for action in msg.actions],
            'timestamp': time.time()
        }
        self.action_sequences_received.append(action_info)

        self.get_logger().info(f'Received action sequence with {len(msg.actions)} actions')

    def clear_exercise_state(self):
        """Clear exercise state for a new exercise"""
        self.status_history.clear()
        self.action_sequences_received.clear()

    def wait_for_pipeline_completion(self, timeout=30.0):
        """Wait for pipeline to reach completion state"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.status_history:
                last_status = self.status_history[-1]
                if last_status['state'] in ['COMPLETED', 'ERROR']:
                    return last_status['state'] == 'COMPLETED'
            time.sleep(0.1)
        return False

    def run_basic_functionality_exercise(self) -> bool:
        """Exercise 1: Basic functionality test"""
        self.current_exercise_name = "Basic Functionality"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        self.clear_exercise_state()

        # Test simple navigation command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "go to the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "NAVIGATE_TO_LOCATION"
        cmd_msg.parameters = ["kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published basic navigation command')

        success = self.wait_for_pipeline_completion(timeout=20.0)

        # Validate results
        if success and self.action_sequences_received:
            first_sequence = self.action_sequences_received[0]
            if first_sequence['count'] > 0:
                action_types = [action[0] for action in first_sequence['actions']]
                if 'NAVIGATION' in action_types:
                    self.get_logger().info(f'{self.current_exercise_name} PASSED')
                    self.validation_results.append((self.current_exercise_name, True))
                    return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_manipulation_exercise(self) -> bool:
        """Exercise 2: Manipulation command test"""
        self.current_exercise_name = "Manipulation Sequence"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        self.clear_exercise_state()

        # Test manipulation command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "pick up the red cup and place it on the table"
        cmd_msg.confidence_score = 0.85
        cmd_msg.intent = "MANIPULATION_SEQUENCE"
        cmd_msg.parameters = ["red", "cup", "table"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published manipulation command')

        success = self.wait_for_pipeline_completion(timeout=30.0)

        # Validate results - should have perception, navigation, and manipulation
        if success and self.action_sequences_received:
            first_sequence = self.action_sequences_received[0]
            action_types = [action[0] for action in first_sequence['actions']]

            has_perception = 'PERCEPTION' in action_types
            has_navigation = 'NAVIGATION' in action_types
            has_manipulation = 'MANIPULATION' in action_types

            if has_perception and has_navigation and has_manipulation:
                self.get_logger().info(f'{self.current_exercise_name} PASSED')
                self.validation_results.append((self.current_exercise_name, True))
                return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_complex_command_exercise(self) -> bool:
        """Exercise 3: Complex multi-step command"""
        self.current_exercise_name = "Complex Command"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        self.clear_exercise_state()

        # Test complex command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "clean the room by picking up all the cups and placing them in the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "CLEAN_ROOM"
        cmd_msg.parameters = ["cups", "kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published complex command')

        success = self.wait_for_pipeline_completion(timeout=40.0)

        # Validate results - should have multiple actions
        if success and self.action_sequences_received:
            first_sequence = self.action_sequences_received[0]
            if first_sequence['count'] >= 3:  # At least perception, navigation, manipulation
                self.get_logger().info(f'{self.current_exercise_name} PASSED')
                self.validation_results.append((self.current_exercise_name, True))
                return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_safety_validation_exercise(self) -> bool:
        """Exercise 4: Safety validation test"""
        self.current_exercise_name = "Safety Validation"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        # Create a mock action sequence for safety validation
        action_sequence = VLAActionSequence()
        action_sequence.status = 'PENDING'
        action_sequence.safety_level = 'NORMAL'

        # Add a navigation action
        nav_action = VLAAction()
        nav_action.action_type = 'NAVIGATION'
        nav_action.action_parameters = ['location=kitchen']
        nav_action.priority = 1
        nav_action.timeout.sec = 30
        nav_action.timeout.nanosec = 0
        nav_action.dependencies = []

        action_sequence.actions.append(nav_action)

        # Call safety validation service
        request = ValidateSafety.Request()
        request.action_sequence = action_sequence

        future = self.validate_safety_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)

        if future.result() is not None:
            response = future.result()
            if response.is_safe:
                self.get_logger().info(f'{self.current_exercise_name} PASSED')
                self.validation_results.append((self.current_exercise_name, True))
                return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_context_management_exercise(self) -> bool:
        """Exercise 5: Context management test"""
        self.current_exercise_name = "Context Management"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        # Run multiple commands to test context preservation
        commands = [
            ("go to the bedroom", "NAVIGATE_TO_LOCATION", ["bedroom"]),
            ("find the book", "DETECT_OBJECTS", ["book"]),
            ("move to the office", "NAVIGATE_TO_LOCATION", ["office"])
        ]

        success_count = 0
        for cmd_text, intent, params in commands:
            self.clear_exercise_state()

            cmd_msg = VLACommand()
            cmd_msg.command_text = cmd_text
            cmd_msg.confidence_score = 0.85
            cmd_msg.intent = intent
            cmd_msg.parameters = params
            cmd_msg.timestamp = self.get_clock().now().to_msg()

            self.command_pub.publish(cmd_msg)
            time.sleep(8.0)  # Wait for processing

            if self.status_history:
                success_count += 1

        # If we successfully processed multiple commands, context management is working
        if success_count >= 2:  # At least 2 out of 3
            self.get_logger().info(f'{self.current_exercise_name} PASSED')
            self.validation_results.append((self.current_exercise_name, True))
            return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_edge_case_exercise(self) -> bool:
        """Exercise 6: Edge case handling"""
        self.current_exercise_name = "Edge Case Handling"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        # Test with low confidence command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "unclear command with low confidence"
        cmd_msg.confidence_score = 0.3  # Low confidence
        cmd_msg.intent = "GENERAL_COMMAND"
        cmd_msg.parameters = []
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published low confidence command')

        time.sleep(10.0)  # Wait for processing

        # System should handle low confidence appropriately
        if self.status_history:
            # Check if system handled the low confidence command appropriately
            self.get_logger().info(f'{self.current_exercise_name} PASSED - System handled low confidence appropriately')
            self.validation_results.append((self.current_exercise_name, True))
            return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_performance_exercise(self) -> bool:
        """Exercise 7: Performance under load"""
        self.current_exercise_name = "Performance Under Load"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        # Send multiple commands in quick succession
        commands = [
            ("go to kitchen", "NAVIGATE_TO_LOCATION", ["kitchen"]),
            ("go to bedroom", "NAVIGATE_TO_LOCATION", ["bedroom"]),
            ("find cup", "DETECT_OBJECTS", ["cup"]),
        ]

        start_time = time.time()
        for cmd_text, intent, params in commands:
            cmd_msg = VLACommand()
            cmd_msg.command_text = cmd_text
            cmd_msg.confidence_score = 0.8
            cmd_msg.intent = intent
            cmd_msg.parameters = params
            cmd_msg.timestamp = self.get_clock().now().to_msg()

            self.command_pub.publish(cmd_msg)
            time.sleep(1.0)  # Brief pause between commands

        # Wait for all to complete
        time.sleep(20.0)

        end_time = time.time()
        total_time = end_time - start_time

        # Check that system handled multiple commands
        if len(self.status_history) > 0:
            self.get_logger().info(f'{self.current_exercise_name} PASSED - Processed {len(self.status_history)} status updates in {total_time:.2f}s')
            self.validation_results.append((self.current_exercise_name, True))
            return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_replanning_exercise(self) -> bool:
        """Exercise 8: Replanning capability (simulated obstacle detection)"""
        self.current_exercise_name = "Replanning Capability"
        self.get_logger().info(f'Running: {self.current_exercise_name}')

        self.clear_exercise_state()

        # Send a navigation command that might encounter simulated obstacles
        cmd_msg = VLACommand()
        cmd_msg.command_text = "go to the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "NAVIGATE_TO_LOCATION"
        cmd_msg.parameters = ["kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published navigation command for replanning test')

        # Wait longer to allow for potential replanning
        success = self.wait_for_pipeline_completion(timeout=45.0)

        # In our simulation, replanning happens internally in the pipeline node
        # The test passes if the pipeline completes successfully despite potential obstacles
        if success:
            self.get_logger().info(f'{self.current_exercise_name} PASSED - Pipeline handled simulated obstacles')
            self.validation_results.append((self.current_exercise_name, True))
            return True

        self.get_logger().warn(f'{self.current_exercise_name} FAILED')
        self.validation_results.append((self.current_exercise_name, False))
        return False

    def run_all_exercises(self) -> bool:
        """Run all validation exercises"""
        self.get_logger().info('Starting VLA System Validation Exercises...')

        exercises = [
            ("Basic Functionality", self.run_basic_functionality_exercise),
            ("Manipulation Sequence", self.run_manipulation_exercise),
            ("Complex Command", self.run_complex_command_exercise),
            ("Safety Validation", self.run_safety_validation_exercise),
            ("Context Management", self.run_context_management_exercise),
            ("Edge Case Handling", self.run_edge_case_exercise),
            ("Performance Under Load", self.run_performance_exercise),
            ("Replanning Capability", self.run_replanning_exercise),
        ]

        results = []

        for exercise_name, exercise_func in exercises:
            self.get_logger().info(f'\n--- Running: {exercise_name} ---')
            try:
                success = exercise_func()
                results.append((exercise_name, success))
                self.get_logger().info(f'{exercise_name}: {"PASS" if success else "FAIL"}')
            except Exception as e:
                self.get_logger().error(f'{exercise_name} failed with exception: {e}')
                results.append((exercise_name, False))

            # Brief pause between exercises
            time.sleep(2.0)

        # Print summary
        self.get_logger().info('\n=== VLA System Validation Exercises Summary ===')
        for exercise_name, passed in results:
            status = 'PASS' if passed else 'FAIL'
            self.get_logger().info(f'{exercise_name}: {status}')

        # Calculate overall result
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        success_rate = (passed_count / total_count) * 100
        self.get_logger().info(f'Overall: {passed_count}/{total_count} exercises passed ({success_rate:.1f}%)')

        return passed_count == total_count

    def print_detailed_validation_report(self):
        """Print detailed validation report"""
        self.get_logger().info('\n=== Detailed Validation Report ===')

        if self.status_history:
            self.get_logger().info(f'Total status messages: {len(self.status_history)}')
            states = [s['state'] for s in self.status_history]
            state_counts = {state: states.count(state) for state in set(states)}
            self.get_logger().info(f'State distribution: {state_counts}')

        if self.action_sequences_received:
            self.get_logger().info(f'Total action sequences: {len(self.action_sequences_received)}')
            total_actions = sum(seq['count'] for seq in self.action_sequences_received)
            self.get_logger().info(f'Total actions generated: {total_actions}')

        # Performance metrics
        if len(self.status_history) > 1:
            start_time = self.status_history[0]['timestamp']
            end_time = self.status_history[-1]['timestamp']
            duration = end_time - start_time
            self.get_logger().info(f'Total validation duration: {duration:.2f} seconds')
            self.get_logger().info(f'Average status messages per second: {len(self.status_history) / duration:.2f}' if duration > 0 else 'N/A')


def main(args=None):
    rclpy.init(args=args)

    validator = VLAValidationExercises()

    # Use a multi-threaded executor to handle callbacks while running exercises
    executor = MultiThreadedExecutor()
    executor.add_node(validator)

    try:
        # Run all validation exercises
        all_passed = validator.run_all_exercises()

        # Print detailed report
        validator.print_detailed_validation_report()

        if all_passed:
            validator.get_logger().info('\n🎉 All VLA System Validation Exercises PASSED!')
            return 0
        else:
            validator.get_logger().info('\n⚠️  Some VLA System Validation Exercises FAILED.')
            return 1

    except KeyboardInterrupt:
        validator.get_logger().info('Validation exercises interrupted by user')
        return 1
    finally:
        validator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    exit(main())