#!/usr/bin/env python3
"""
LLM Planner Testing Script for VLA System

This script tests the LLM-based cognitive planning functionality by simulating
natural language commands and verifying the generated action sequences.
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import time
import threading
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction
from vla_interfaces.srv import PlanActions
from std_msgs.msg import String


class LLMPlannerTester(Node):
    def __init__(self):
        super().__init__('llm_planner_tester')

        # Create publisher for VLA commands
        self.command_pub = self.create_publisher(
            VLACommand,
            '/vla/command',
            10
        )

        # Create subscriber to listen for action sequences
        self.action_sequence_sub = self.create_subscription(
            VLAActionSequence,
            '/vla/action_sequence',
            self.action_sequence_callback,
            10
        )

        # Create client for plan actions service
        self.plan_actions_client = self.create_client(
            PlanActions,
            '/vla/plan_actions'
        )

        # Wait for service to be available
        while not self.plan_actions_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Plan actions service not available, waiting...')

        # Test results
        self.last_action_sequence = None
        self.test_results = []

        self.get_logger().info('LLM Planner tester initialized')

    def action_sequence_callback(self, msg):
        """Callback for received action sequences"""
        self.last_action_sequence = msg
        self.get_logger().info(f'Received action sequence with {len(msg.actions)} actions')
        for i, action in enumerate(msg.actions):
            self.get_logger().info(f'  Action {i+1}: {action.action_type} - {action.action_parameters}')

    def test_navigation_command(self):
        """Test navigation command processing"""
        self.get_logger().info('Testing navigation command: "go to the kitchen"')

        # Create and publish command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "go to the kitchen"
        cmd_msg.confidence_score = 0.9
        cmd_msg.intent = "NAVIGATE_TO_LOCATION"
        cmd_msg.parameters = ["kitchen"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published navigation command')

        # Wait for response
        time.sleep(3.0)

        if self.last_action_sequence and len(self.last_action_sequence.actions) > 0:
            # Check if the first action is a navigation action
            first_action = self.last_action_sequence.actions[0]
            if first_action.action_type == 'NAVIGATION':
                self.get_logger().info('Navigation test passed')
                return True
            else:
                self.get_logger().warn(f'Expected NAVIGATION action, got {first_action.action_type}')
                return False
        else:
            self.get_logger().warn('Navigation test failed: No action sequence received')
            return False

    def test_manipulation_command(self):
        """Test manipulation command processing"""
        self.get_logger().info('Testing manipulation command: "pick up the red cup"')

        # Create and publish command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "pick up the red cup"
        cmd_msg.confidence_score = 0.85
        cmd_msg.intent = "PICK_UP_OBJECT"
        cmd_msg.parameters = ["red", "cup"]
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published manipulation command')

        # Wait for response
        time.sleep(4.0)

        if self.last_action_sequence and len(self.last_action_sequence.actions) > 0:
            # Check if we have perception, navigation, and manipulation actions
            action_types = [action.action_type for action in self.last_action_sequence.actions]
            has_perception = 'PERCEPTION' in action_types
            has_navigation = 'NAVIGATION' in action_types
            has_manipulation = 'MANIPULATION' in action_types

            if has_perception and has_navigation and has_manipulation:
                self.get_logger().info('Manipulation test passed')
                return True
            else:
                self.get_logger().warn(f'Manipulation test failed: Missing action types. Found: {action_types}')
                return False
        else:
            self.get_logger().warn('Manipulation test failed: No action sequence received')
            return False

    def test_service_call(self):
        """Test the plan actions service directly"""
        self.get_logger().info('Testing plan actions service...')

        # Create request
        request = PlanActions.Request()
        request.command_text = "find the blue ball"
        request.intent = "DETECT_OBJECTS"
        request.parameters = ["blue", "ball"]

        # Make service call
        future = self.plan_actions_client.call_async(request)

        # Wait for response
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)

        if future.result() is not None:
            response = future.result()
            if response.success and len(response.action_sequence.actions) > 0:
                self.get_logger().info(f'Service test passed: Generated {len(response.action_sequence.actions)} actions')

                # Check if the first action is perception
                first_action = response.action_sequence.actions[0]
                if first_action.action_type == 'PERCEPTION':
                    self.get_logger().info('Service test passed: Correct action type')
                    return True
                else:
                    self.get_logger().warn(f'Service test failed: Expected PERCEPTION, got {first_action.action_type}')
                    return False
            else:
                self.get_logger().warn(f'Service test failed: {response.error_message}')
                return False
        else:
            self.get_logger().warn('Service call failed or timed out')
            return False

    def test_complex_command(self):
        """Test a complex multi-step command"""
        self.get_logger().info('Testing complex command: "clean the room"')

        # Create and publish command
        cmd_msg = VLACommand()
        cmd_msg.command_text = "clean the room"
        cmd_msg.confidence_score = 0.95
        cmd_msg.intent = "CLEAN_ROOM"
        cmd_msg.parameters = []
        cmd_msg.timestamp = self.get_clock().now().to_msg()

        self.command_pub.publish(cmd_msg)
        self.get_logger().info('Published complex command')

        # Wait for response
        time.sleep(5.0)

        if self.last_action_sequence and len(self.last_action_sequence.actions) >= 3:
            # Complex commands should generate multiple actions
            self.get_logger().info(f'Complex command test passed: Generated {len(self.last_action_sequence.actions)} actions')
            return True
        else:
            self.get_logger().warn(f'Complex command test failed: Expected >= 3 actions, got {len(self.last_action_sequence.actions) if self.last_action_sequence else 0}')
            return False

    def run_all_tests(self):
        """Run all LLM planner tests"""
        self.get_logger().info('Starting LLM Planner system tests...')

        results = []

        # Reset last action sequence before each test
        self.last_action_sequence = None

        # Test 1: Navigation command
        self.get_logger().info('\nTest 1: Navigation Command')
        result1 = self.test_navigation_command()
        results.append(('Navigation Command', result1))

        # Reset for next test
        self.last_action_sequence = None
        time.sleep(1.0)

        # Test 2: Manipulation command
        self.get_logger().info('\nTest 2: Manipulation Command')
        result2 = self.test_manipulation_command()
        results.append(('Manipulation Command', result2))

        # Reset for next test
        self.last_action_sequence = None
        time.sleep(1.0)

        # Test 3: Service call
        self.get_logger().info('\nTest 3: Service Call')
        result3 = self.test_service_call()
        results.append(('Service Call', result3))

        # Reset for next test
        self.last_action_sequence = None
        time.sleep(1.0)

        # Test 4: Complex command
        self.get_logger().info('\nTest 4: Complex Command')
        result4 = self.test_complex_command()
        results.append(('Complex Command', result4))

        # Print summary
        self.get_logger().info('\n=== LLM Planner Test Results Summary ===')
        for test_name, passed in results:
            status = 'PASS' if passed else 'FAIL'
            self.get_logger().info(f'{test_name}: {status}')

        # Calculate overall result
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        self.get_logger().info(f'Overall: {passed_count}/{total_count} tests passed')

        return passed_count == total_count


def main(args=None):
    rclpy.init(args=args)

    tester = LLMPlannerTester()

    # Use a multi-threaded executor to handle callbacks while running tests
    executor = MultiThreadedExecutor()
    executor.add_node(tester)

    try:
        # Run all tests
        all_passed = tester.run_all_tests()

        if all_passed:
            tester.get_logger().info('All LLM Planner tests passed!')
        else:
            tester.get_logger().info('Some LLM Planner tests failed.')

    except KeyboardInterrupt:
        tester.get_logger().info('Test interrupted by user')
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()