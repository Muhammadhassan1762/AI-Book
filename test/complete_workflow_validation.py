#!/usr/bin/env python3
"""
Complete Workflow Validation Script

This script validates the complete workflow from installation to simulation validation
for the Digital Twin (Gazebo & Unity) module.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("Checking prerequisites...")

    checks = {
        'ROS 2 Humble': check_ros2_humble(),
        'Gazebo Garden': check_gazebo_garden(),
        'Python 3.8+': check_python_version(),
        'Git': check_git_installed(),
    }

    all_passed = True
    for check_name, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False

    return all_passed


def check_ros2_humble():
    """Check if ROS 2 Humble is installed"""
    try:
        result = subprocess.run(['ros2', '--version'], capture_output=True, text=True, timeout=5)
        return 'humble' in result.stdout.lower()
    except:
        return False


def check_gazebo_garden():
    """Check if Gazebo Garden is installed"""
    try:
        result = subprocess.run(['gazebo', '--version'], capture_output=True, text=True, timeout=5)
        return 'garden' in result.stdout.lower()
    except:
        return False


def check_python_version():
    """Check if Python 3.8+ is installed"""
    return sys.version_info >= (3, 8)


def check_git_installed():
    """Check if Git is installed"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def validate_directory_structure():
    """Validate that the expected directory structure exists"""
    print("Validating directory structure...")

    required_paths = [
        'docs/digital-twin',
        'simulation/gazebo/worlds',
        'simulation/gazebo/models',
        'simulation/gazebo/launch',
        'simulation/unity/Assets/Scenes',
        'simulation/unity/Assets/Scripts',
        'simulation/ros_integration/config',
        'simulation/ros_integration/launch',
    ]

    all_exist = True
    for path in required_paths:
        exists = Path(path).exists()
        status = "EXISTS" if exists else "MISSING"
        print(f"  {path}: {status}")
        if not exists:
            all_exist = False

    return all_exist


def validate_documentation():
    """Validate that documentation files exist and have content"""
    print("Validating documentation...")

    required_docs = [
        'docs/digital-twin/index.md',
        'docs/digital-twin/chapter-1-physics-sim/index.md',
        'docs/digital-twin/chapter-2-visual-interaction/index.md',
        'docs/digital-twin/chapter-3-sensor-sim/index.md',
        'docs/digital-twin/quickstart.md',
    ]

    all_valid = True
    for doc_path in required_docs:
        if Path(doc_path).exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_content = len(content.strip()) > 0
                status = "VALID" if has_content else "EMPTY"
                print(f"  {doc_path}: {status}")
                if not has_content:
                    all_valid = False
        else:
            print(f"  {doc_path}: MISSING")
            all_valid = False

    return all_valid


def validate_simulation_models():
    """Validate that simulation models exist and are properly configured"""
    print("Validating simulation models...")

    required_models = [
        'simulation/gazebo/models/simple_humanoid/model.sdf',
        'simulation/gazebo/models/simple_humanoid/model.config',
        'simulation/gazebo/models/sensor_equipped_robot/model.sdf',
        'simulation/gazebo/models/sensor_equipped_robot/model.config',
    ]

    required_worlds = [
        'simulation/gazebo/worlds/basic_physics.world',
        'simulation/gazebo/worlds/sensor_test.world',
        'simulation/gazebo/worlds/humanoid_validation.world',
    ]

    all_valid = True

    for model_path in required_models + required_worlds:
        if Path(model_path).exists():
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_content = len(content.strip()) > 0
                status = "VALID" if has_content else "EMPTY"
                print(f"  {model_path}: {status}")
                if not has_content:
                    all_valid = False
        else:
            print(f"  {model_path}: MISSING")
            all_valid = False

    return all_valid


def validate_ros_launch_files():
    """Validate that ROS launch files exist and are properly configured"""
    print("Validating ROS launch files...")

    required_launch_files = [
        'simulation/gazebo/launch/physics_demo.launch.py',
        'simulation/gazebo/launch/sensor_validation.launch.py',
        'simulation/ros_integration/launch/simulation_bridge.launch.py',
    ]

    all_valid = True
    for launch_path in required_launch_files:
        if Path(launch_path).exists():
            with open(launch_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_content = len(content.strip()) > 0
                has_python_syntax = 'import' in content and 'def generate_launch_description' in content
                is_valid = has_content and has_python_syntax
                status = "VALID" if is_valid else "INVALID"
                print(f"  {launch_path}: {status}")
                if not is_valid:
                    all_valid = False
        else:
            print(f"  {launch_path}: MISSING")
            all_valid = False

    return all_valid


def validate_config_files():
    """Validate that configuration files exist and are properly formatted"""
    print("Validating configuration files...")

    required_configs = [
        'simulation/ros_integration/config/unity_bridge.yaml',
        'simulation/ros_integration/config/environment_config.yaml',
    ]

    all_valid = True
    for config_path in required_configs:
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_content = len(content.strip()) > 0
                has_yaml_structure = content.strip().startswith('#') or 'ros__parameters:' in content
                is_valid = has_content and has_yaml_structure
                status = "VALID" if is_valid else "INVALID"
                print(f"  {config_path}: {status}")
                if not is_valid:
                    all_valid = False
        else:
            print(f"  {config_path}: MISSING")
            all_valid = False

    return all_valid


def validate_test_scripts():
    """Validate that test scripts exist and are properly configured"""
    print("Validating test scripts...")

    required_tests = [
        'simulation/gazebo/test/physics_validation_test.py',
        'simulation/gazebo/test/real_world_physics_validation.py',
        'simulation/gazebo/test/lidar_validation_test.py',
        'simulation/gazebo/test/camera_imu_validation_test.py',
        'simulation/gazebo/test/sensor_output_validation.py',
    ]

    all_valid = True
    for test_path in required_tests:
        if Path(test_path).exists():
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_content = len(content.strip()) > 0
                has_python_syntax = 'import rclpy' in content and 'class' in content
                is_valid = has_content and has_python_syntax
                status = "VALID" if is_valid else "INVALID"
                print(f"  {test_path}: {status}")
                if not is_valid:
                    all_valid = False
        else:
            print(f"  {test_path}: MISSING")
            all_valid = False

    return all_valid


def validate_reading_level():
    """Validate that content meets Grade 10-12 reading level requirements (basic check)"""
    print("Validating content reading level (basic check)...")

    # This is a very basic check - in a real implementation, we would use
    # more sophisticated readability analysis tools
    docs_to_check = [
        'docs/digital-twin/index.md',
        'docs/digital-twin/chapter-1-physics-sim/index.md',
        'docs/digital-twin/chapter-2-visual-interaction/index.md',
        'docs/digital-twin/chapter-3-sensor-sim/index.md',
    ]

    all_meet_requirements = True

    for doc_path in docs_to_check:
        if Path(doc_path).exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Basic checks for Grade 10-12 level:
                # - Clear headings and structure
                # - Explanatory content
                # - Not overly technical without explanation
                has_headings = '#' in content
                has_explanations = 'This section' in content or 'This chapter' in content or 'Learn how' in content
                has_examples = '```' in content or 'Example:' in content or 'For example' in content

                meets_level = has_headings and (has_explanations or has_examples)
                status = "MEETS" if meets_level else "MAY NOT MEET"
                print(f"  {doc_path}: {status}")

                if not meets_level:
                    all_meet_requirements = False
        else:
            print(f"  {doc_path}: MISSING")
            all_meet_requirements = False

    return all_meet_requirements


def run_complete_validation():
    """Run the complete workflow validation"""
    print("=" * 60)
    print("DIGITAL TWIN (GAZEBO & UNITY) COMPLETE WORKFLOW VALIDATION")
    print("=" * 60)

    # Run all validation checks
    results = {
        'Prerequisites': check_prerequisites(),
        'Directory Structure': validate_directory_structure(),
        'Documentation': validate_documentation(),
        'Simulation Models': validate_simulation_models(),
        'ROS Launch Files': validate_ros_launch_files(),
        'Configuration Files': validate_config_files(),
        'Test Scripts': validate_test_scripts(),
        'Reading Level': validate_reading_level(),
    }

    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    all_passed = True
    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{check_name:.<40} {status}")
        if not result:
            all_passed = False

    print("=" * 60)
    overall_status = "ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED"
    print(f"OVERALL STATUS: {overall_status}")
    print("=" * 60)

    return all_passed


def main():
    success = run_complete_validation()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()