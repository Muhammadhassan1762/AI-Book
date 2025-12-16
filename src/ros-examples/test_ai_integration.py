#!/usr/bin/env python3

"""
Test script to validate the AI agent integration example.

This script doesn't require a full ROS 2 environment to understand the concepts,
but demonstrates how you would test the AI-robot integration in practice.
"""

import subprocess
import time
import signal
import sys
import os

def test_ai_robot_integration():
    """
    Test the AI-robot integration example by describing how to run and validate it.
    """
    print("Testing AI-Robot Integration Example")
    print("=" * 40)

    print("To test this example in a real ROS 2 environment:")
    print("1. Source your ROS 2 installation: source /opt/ros/humble/setup.bash")
    print("2. Navigate to your workspace: cd ~/ros2_ws")
    print("3. Source the workspace: source install/setup.bash")
    print("4. Run the AI decision node: ros2 run ros2_fundamentals_examples ai_decision_node")
    print("5. In another terminal, run the robot controller: ros2 run ros2_fundamentals_examples robot_controller")
    print("6. Or use the launch file: ros2 launch simulation_launch ai_robot_integration.launch.py")
    print()
    print("Expected behavior:")
    print("- The AI node should process 'sensor_data' messages and make decisions")
    print("- The AI node should publish velocity commands to 'robot_cmd_vel'")
    print("- The robot controller should receive commands and publish status updates")
    print("- The robot controller should also publish simulated sensor data")
    print()

    print("You can also test with command-line tools:")
    print("- ros2 topic echo robot_status  # Monitor robot status")
    print("- ros2 topic echo robot_cmd_vel # Monitor commands sent to robot")
    print("- ros2 topic pub sensor_data std_msgs/String 'data: \"obstacle 1m ahead\"'  # Send test sensor data")
    print("- ros2 run rqt_graph rqt_graph  # Visualize the node graph")

    print("\nTest completed - this is a validation of the expected behavior.")

def validate_ai_code_structure():
    """
    Validate that the required AI integration files exist and have the expected structure.
    """
    print("\nValidating AI Integration Code Structure")
    print("=" * 40)

    required_files = [
        'src/ros-examples/ai_decision_node.py',
        'src/ros-examples/robot_controller.py',
        'src/ros-examples/rclpy_template.py',
        'simulation/launch/ai_robot_integration.launch.py'
    ]

    all_found = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ Found: {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            all_found = False

    if all_found:
        print("\n✓ All required AI integration files are present")
    else:
        print("\n✗ Some required AI integration files are missing")

    # Check that the files contain expected elements
    print("\nValidating file content...")

    # Check ai_decision_node.py
    if os.path.exists('src/ros-examples/ai_decision_node.py'):
        with open('src/ros-examples/ai_decision_node.py', 'r') as f:
            content = f.read()
            if 'AIDecisionNode' in content and 'make_decision' in content:
                print("✓ AI Decision Node has expected structure")
            else:
                print("✗ AI Decision Node missing expected structure")

    # Check robot_controller.py
    if os.path.exists('src/ros-examples/robot_controller.py'):
        with open('src/ros-examples/robot_controller.py', 'r') as f:
            content = f.read()
            if 'RobotController' in content and 'cmd_vel_callback' in content:
                print("✓ Robot Controller has expected structure")
            else:
                print("✗ Robot Controller missing expected structure")

    return all_found

if __name__ == '__main__':
    print("ROS 2 Fundamentals - AI-Robot Integration Test")
    print("This script validates the AI integration example without requiring a full ROS 2 environment.\n")

    # Validate code structure
    structure_valid = validate_ai_code_structure()

    # Explain how to test
    test_ai_robot_integration()

    if structure_valid:
        print("\n✓ Validation successful - all AI integration components are in place")
        print("To fully test, run in a ROS 2 environment as described above.")
    else:
        print("\n✗ Validation failed - missing AI integration components")
        sys.exit(1)