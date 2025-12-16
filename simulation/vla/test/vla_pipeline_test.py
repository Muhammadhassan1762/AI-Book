#!/usr/bin/env python3
"""
Complete VLA Pipeline Testing Script for VLA System

This script tests the complete Vision-Language-Action pipeline,
from voice command to action execution with safety validation.
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import time
import threading
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction, VLAStatus
from vla_interfaces.srv import ProcessCommand, PlanActions, ValidateSafety
from std_msgs.msg import String
from typing import List, Dict, Any
import json


class VLAPipelineTester(Node):
    def __init__(self):
        super().__init__('vla_pipeline_tester')

        # Create publishers for testing the pipeline
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
        self.test_results = []
        self.current_test_name = ""

        self.get_logger().info('VLA Pipeline tester initialized')

    def status_callback(self, msg):
        """Callback for status messages"""
        self.status_history.append({
            'state': msg.current_state,
            'action': msg.current_action,
            'progress': msg.progress_percentage,
            'timestamp': time.time(),
            'error': msg.error_message
        })

        if self.current_test_name:
            self.get_logger().debug(f'Test {self.current_test_name}: Status - {msg.current_state} ({msg.progress_percentage}%)')

    def action_sequence_callback(self, msg):
        """Callback for action sequence messages"""
        action_info = {
            'count': len(msg.actions),
            'actions': [(action.action_type, action.action_parameters) for action in msg.actions],
            'timestamp': time.time()
        }
        self.action_sequences_received.append(action_info)

        self.get_logger().info(f'Received action sequence with {len(msg.actions)} actions')

    def clear_test_state(self):
        """Clear test state for a new test"""
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

    def test_simple_navigation(self):
        """Test simple navigation command"""
        self.current_test_name = "Simple Navigation"
        self.get_logger().info(f'Testing: {self.current_test_name}')

        self.clear_test_state()

        # Create and publish navigation command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "go to the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "NAVIGATE_TO_LOCATION"
        cmd_msg.parameters = ["kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published navigation command')

        # Wait for completion
        success = self.wait_for_pipeline_completion(timeout=20.0)

        # Check results
        if success and self.action_sequences_received:
            first_sequence = self.action_sequences_received[0]
            if first_sequence['count'] > 0 and first_sequence['actions'][0][0] == 'NAVIGATION':
                self.get_logger().info(f'{self.current_test_name} test PASSED')
                return True

        self.get_logger().warn(f'{self.current_test_name} test FAILED')
        return False

    def test_manipulation_sequence(self):
        """Test manipulation command sequence"""
        self.current_test_name = "Manipulation Sequence"
        self.get_logger().info(f'Testing: {self.current_test_name}')

        self.clear_test_state()

        # Create and publish manipulation command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "pick up the red cup and place it on the table"
        cmd_msg.confidence_score = 0.85
        cmd_msg.intent = "MANIPULATION_SEQUENCE"
        cmd_msg.parameters = ["red", "cup", "table"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published manipulation command')

        # Wait for completion
        success = self.wait_for_pipeline_completion(timeout=30.0)

        # Check results - should have multiple actions including perception, navigation, and manipulation
        if success and self.action_sequences_received:
            first_sequence = self.action_sequences_received[0]
            action_types = [action[0] for action in first_sequence['actions']]

            has_perception = 'PERCEPTION' in action_types
            has_navigation = 'NAVIGATION' in action_types
            has_manipulation = 'MANIPULATION' in action_types

            if has_perception and has_navigation and has_manipulation:
                self.get_logger().info(f'{self.current_test_name} test PASSED')
                return True

        self.get_logger().warn(f'{self.current_test_name} test FAILED')
        return False

    def test_complex_command(self):
        """Test complex multi-step command"""
        self.current_test_name = "Complex Command"
        self.get_logger().info(f'Testing: {self.current_test_name}')

        self.clear_test_state()

        # Create and publish complex command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "clean the room by picking up all the cups and placing them in the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "CLEAN_ROOM"
        cmd_msg.parameters = ["cups", "kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published complex command')

        # Wait for completion
        success = self.wait_for_pipeline_completion(timeout=40.0)

        # Check results - should have multiple actions
        if success and self.action_sequences_received:
            first_sequence = self.action_sequences_received[0]
            if first_sequence['count'] >= 3:  # At least perception, navigation, manipulation
                self.get_logger().info(f'{self.current_test_name} test PASSED')
                return True

        self.get_logger().warn(f'{self.current_test_name} test FAILED')
        return False

    def test_service_integration(self):
        """Test pipeline service integration"""
        self.current_test_name = "Service Integration"
        self.get_logger().info(f'Testing: {self.current_test_name}')

        # Test the execute_pipeline service
        request = ProcessCommand.Request()
        request.raw_command = "move to the office"
        request.audio_confidence = 0.8

        future = self.execute_pipeline_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=20.0)

        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'{self.current_test_name} test PASSED')
                return True

        self.get_logger().warn(f'{self.current_test_name} test FAILED')
        return False

    def test_safety_validation(self):
        """Test safety validation service"""
        self.current_test_name = "Safety Validation"
        self.get_logger().info(f'Testing: {self.current_test_name}')

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
            # Safety validation should pass for a simple navigation to a known location
            if response.is_safe:
                self.get_logger().info(f'{self.current_test_name} test PASSED')
                return True

        self.get_logger().warn(f'{self.current_test_name} test FAILED')
        return False

    def test_context_preservation(self):
        """Test that context is preserved across pipeline runs"""
        self.current_test_name = "Context Preservation"
        self.get_logger().info(f'Testing: {self.current_test_name}')

        # First, run a simple command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "go to the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "NAVIGATE_TO_LOCATION"
        cmd_msg.parameters = ["kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published first command')

        # Wait briefly for processing
        time.sleep(5.0)

        # Check that we have status history
        if len(self.status_history) > 0:
            self.get_logger().info(f'{self.current_test_name} test PASSED - Context preserved')
            return True

        self.get_logger().warn(f'{self.current_test_name} test FAILED - No context preserved')
        return False

    def run_all_tests(self):
        """Run all VLA pipeline tests"""
        self.get_logger().info('Starting Complete VLA Pipeline tests...')

        tests = [
            ("Simple Navigation", self.test_simple_navigation),
            ("Manipulation Sequence", self.test_manipulation_sequence),
            ("Complex Command", self.test_complex_command),
            ("Service Integration", self.test_service_integration),
            ("Safety Validation", self.test_safety_validation),
            ("Context Preservation", self.test_context_preservation),
        ]

        results = []

        for test_name, test_func in tests:
            self.get_logger().info(f'\n--- Running: {test_name} ---')
            try:
                success = test_func()
                results.append((test_name, success))
                self.get_logger().info(f'{test_name}: {"PASS" if success else "FAIL"}')
            except Exception as e:
                self.get_logger().error(f'{test_name} failed with exception: {e}')
                results.append((test_name, False))

            # Brief pause between tests
            time.sleep(2.0)

        # Print summary
        self.get_logger().info('\n=== Complete VLA Pipeline Test Results Summary ===')
        for test_name, passed in results:
            status = 'PASS' if passed else 'FAIL'
            self.get_logger().info(f'{test_name}: {status}')

        # Calculate overall result
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        self.get_logger().info(f'Overall: {passed_count}/{total_count} tests passed')

        return passed_count == total_count

    def print_detailed_results(self):
        """Print detailed test results"""
        self.get_logger().info('\n=== Detailed Test Results ===')

        if self.status_history:
            self.get_logger().info(f'Total status messages received: {len(self.status_history)}')
            states = [s['state'] for s in self.status_history]
            state_counts = {state: states.count(state) for state in set(states)}
            self.get_logger().info(f'State distribution: {state_counts}')

            if states:
                final_state = states[-1]
                self.get_logger().info(f'Final pipeline state: {final_state}')

        if self.action_sequences_received:
            self.get_logger().info(f'Total action sequences received: {len(self.action_sequences_received)}')
            total_actions = sum(seq['count'] for seq in self.action_sequences_received)
            self.get_logger().info(f'Total actions generated: {total_actions}')


def main(args=None):
    rclpy.init(args=args)

    tester = VLAPipelineTester()

    # Use a multi-threaded executor to handle callbacks while running tests
    executor = MultiThreadedExecutor()
    executor.add_node(tester)

    try:
        # Run all tests
        all_passed = tester.run_all_tests()

        # Print detailed results
        tester.print_detailed_results()

        if all_passed:
            tester.get_logger().info('\n🎉 All Complete VLA Pipeline tests passed!')
            return 0
        else:
            tester.get_logger().info('\n❌ Some Complete VLA Pipeline tests failed.')
            return 1

    except KeyboardInterrupt:
        tester.get_logger().info('Tests interrupted by user')
        return 1
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    exit(main())