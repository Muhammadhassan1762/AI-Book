#!/usr/bin/env python3

"""
Test script to validate the URDF model example.

This script doesn't require a full ROS 2 environment to understand the concepts,
but demonstrates how you would test the URDF model in practice.
"""

import subprocess
import time
import signal
import sys
import os
import xml.etree.ElementTree as ET


def test_urdf_model():
    """
    Test the URDF model by describing how to validate it in ROS 2.
    """
    print("Testing URDF Model Example")
    print("=" * 40)

    print("To test this example in a real ROS 2 environment:")
    print("1. Source your ROS 2 installation: source /opt/ros/humble/setup.bash")
    print("2. Navigate to your workspace: cd ~/ros2_ws")
    print("3. Source the workspace: source install/setup.bash")
    print("4. Run the URDF parser: ros2 run ros2_fundamentals_examples urdf_parser")
    print("5. Or use the visualization launch: ros2 launch simulation_launch urdf_visualization.launch.py")
    print()
    print("Expected behavior:")
    print("- The URDF parser should load and parse the model.urdf file")
    print("- Robot description should be published to /robot_description topic")
    print("- Robot information should be published to /robot_info topic")
    print("- RViz2 should display the robot model with all links and joints")
    print()

    print("You can also test with command-line tools:")
    print("- check_urdf simulation/models/simple_humanoid/model.urdf  # Validate URDF syntax")
    print("- urdf_to_graphiz simulation/models/simple_humanoid/model.urdf  # Generate kinematic tree image")
    print("- ros2 run rviz2 rviz2  # Visualize the robot model")
    print("- ros2 topic echo robot_info  # Monitor parsed robot information")
    print("- ros2 param set /robot_state_publisher robot_description - <urdf_content>  # Load URDF to parameter server")

    print("\nTest completed - this is a validation of the expected behavior.")


def validate_urdf_file():
    """
    Validate the URDF file structure and content.
    """
    print("\nValidating URDF File Structure")
    print("=" * 40)

    urdf_path = "simulation/models/simple_humanoid/model.urdf"

    if not os.path.exists(urdf_path):
        print(f"✗ URDF file not found: {urdf_path}")
        return False

    print(f"✓ Found URDF file: {urdf_path}")

    try:
        # Parse the URDF file
        tree = ET.parse(urdf_path)
        root = tree.getroot()

        # Check if it's a valid robot element
        if root.tag != 'robot':
            print("✗ Root element is not 'robot'")
            return False

        robot_name = root.get('name', 'unnamed')
        print(f"✓ Robot name: {robot_name}")

        # Count links and joints
        links = root.findall('link')
        joints = root.findall('joint')

        print(f"✓ Found {len(links)} links: {[link.get('name') for link in links]}")
        print(f"✓ Found {len(joints)} joints: {[joint.get('name') for joint in joints]}")

        # Validate each link has required elements
        for link in links:
            link_name = link.get('name')

            # Check for visual element
            visual = link.find('visual')
            if visual is None:
                print(f"⚠ Link '{link_name}' has no visual element")
            else:
                print(f"✓ Link '{link_name}' has visual element")

            # Check for collision element
            collision = link.find('collision')
            if collision is None:
                print(f"⚠ Link '{link_name}' has no collision element")
            else:
                print(f"✓ Link '{link_name}' has collision element")

            # Check for inertial element
            inertial = link.find('inertial')
            if inertial is None:
                print(f"⚠ Link '{link_name}' has no inertial element")
            else:
                print(f"✓ Link '{link_name}' has inertial element")

        # Validate each joint
        for joint in joints:
            joint_name = joint.get('name')
            joint_type = joint.get('type')

            parent = joint.find('parent')
            child = joint.find('child')

            if parent is None or child is None:
                print(f"✗ Joint '{joint_name}' missing parent or child")
                continue

            parent_link = parent.get('link')
            child_link = child.get('link')

            print(f"✓ Joint '{joint_name}' ({joint_type}): {parent_link} -> {child_link}")

        print(f"\n✓ URDF validation passed for {robot_name}")
        print(f"  - Total links: {len(links)}")
        print(f"  - Total joints: {len(joints)}")
        return True

    except ET.ParseError as e:
        print(f"✗ Error parsing URDF XML: {e}")
        return False
    except Exception as e:
        print(f"✗ Error validating URDF: {e}")
        return False


def validate_urdf_code_structure():
    """
    Validate that the required URDF integration files exist.
    """
    print("\nValidating URDF Integration Code Structure")
    print("=" * 40)

    required_files = [
        'src/ros-examples/urdf_parser.py',
        'simulation/models/simple_humanoid/model.urdf',
        'simulation/models/simple_humanoid/materials/blue.material',
        'simulation/models/simple_humanoid/materials/red.material',
        'simulation/models/simple_humanoid/materials/green.material',
        'simulation/launch/urdf_visualization.launch.py'
    ]

    all_found = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ Found: {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            all_found = False

    if all_found:
        print("\n✓ All required URDF integration files are present")
    else:
        print("\n✗ Some required URDF integration files are missing")

    return all_found


def check_urdf_syntax(urdf_content):
    """
    Check basic URDF syntax without full ROS validation.
    """
    # Basic checks
    if '<robot' not in urdf_content or '</robot>' not in urdf_content:
        return False, "Missing robot tag"

    if urdf_content.count('<robot') != urdf_content.count('</robot>'):
        return False, "Unmatched robot tags"

    # Check for at least one link
    if '<link' not in urdf_content:
        return False, "No links found"

    # Check for proper XML structure
    try:
        ET.fromstring(urdf_content)
        return True, "Basic syntax appears valid"
    except ET.ParseError as e:
        return False, f"XML parsing error: {e}"


if __name__ == '__main__':
    print("ROS 2 Fundamentals - URDF Model Test")
    print("This script validates the URDF model example without requiring a full ROS 2 environment.\n")

    # Validate URDF file
    urdf_valid = validate_urdf_file()

    # Validate code structure
    structure_valid = validate_urdf_code_structure()

    # Explain how to test
    test_urdf_model()

    if urdf_valid and structure_valid:
        print("\n✓ Validation successful - URDF model is properly structured")
        print("To fully test, run in a ROS 2 environment as described above.")
    else:
        print("\n✗ Validation failed - URDF model needs correction")
        sys.exit(1)