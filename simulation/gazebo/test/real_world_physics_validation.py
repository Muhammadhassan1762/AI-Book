#!/usr/bin/env python3
"""
Real-World Physics Validation Script

This script validates that the simulation physics matches expected real-world behavior
by comparing simulation results to theoretical physics equations.
"""

import math
import time
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Vector3
from gazebo_msgs.srv import GetModelState
from std_srvs.srv import Empty


class RealWorldPhysicsValidation(Node):
    def __init__(self):
        super().__init__('real_world_physics_validation')

        # Variables to store test data
        self.position_history = []
        self.velocity_history = []
        self.time_history = []
        self.start_time = None

        # Create subscribers
        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/robot/physics/state',
            self.odom_callback,
            10
        )

        # Create service clients
        self.get_model_state_client = self.create_client(
            GetModelState,
            '/gazebo/get_model_state'
        )

        self.reset_simulation_client = self.create_client(
            Empty,
            '/gazebo/reset_simulation'
        )

        # Wait for services
        while not self.get_model_state_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for get_model_state service...')

        while not self.reset_simulation_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for reset_simulation service...')

        self.get_logger().info('Real-world physics validation node initialized')

    def odom_callback(self, msg):
        """Callback to receive robot state from Gazebo"""
        current_time = self.get_clock().now().nanoseconds / 1e9  # Convert to seconds

        position = {
            'x': msg.pose.pose.position.x,
            'y': msg.pose.pose.position.y,
            'z': msg.pose.pose.position.z
        }

        velocity = {
            'x': msg.twist.twist.linear.x,
            'y': msg.twist.twist.linear.y,
            'z': msg.twist.twist.linear.z
        }

        self.position_history.append(position)
        self.velocity_history.append(velocity)
        self.time_history.append(current_time)

        # Keep only the last 100 data points to prevent memory issues
        if len(self.position_history) > 100:
            self.position_history.pop(0)
            self.velocity_history.pop(0)
            self.time_history.pop(0)

        if self.start_time is None:
            self.start_time = current_time

    def calculate_acceleration(self):
        """Calculate acceleration from position and velocity data"""
        if len(self.velocity_history) < 2:
            return None

        # Calculate acceleration using velocity differences
        dt = self.time_history[-1] - self.time_history[-2]
        if dt <= 0:
            return None

        dvx = self.velocity_history[-1]['x'] - self.velocity_history[-2]['x']
        dvy = self.velocity_history[-1]['y'] - self.velocity_history[-2]['y']
        dvz = self.velocity_history[-1]['z'] - self.velocity_history[-2]['z']

        ax = dvx / dt if dt != 0 else 0
        ay = dvy / dt if dt != 0 else 0
        az = dvz / dt if dt != 0 else 0

        return {'x': ax, 'y': ay, 'z': az}

    def validate_gravity_acceleration(self):
        """Validate that objects accelerate at 9.81 m/s² due to gravity"""
        acceleration = self.calculate_acceleration()

        if acceleration is None:
            self.get_logger().warn('Not enough data to calculate acceleration')
            return False

        # Check if Z acceleration is close to -9.81 m/s² (negative because of downward gravity)
        expected_gravity = -9.81
        tolerance = 0.1  # Allow 0.1 m/s² tolerance

        gravity_match = abs(acceleration['z'] - expected_gravity) < tolerance

        self.get_logger().info(f'Acceleration: X={acceleration["x"]:.3f}, Y={acceleration["y"]:.3f}, Z={acceleration["z"]:.3f} m/s²')
        self.get_logger().info(f'Expected gravity: {expected_gravity} m/s²')
        self.get_logger().info(f'Gravity validation: {"PASS" if gravity_match else "FAIL"}')

        return gravity_match

    def validate_kinematic_equations(self):
        """Validate that motion follows kinematic equations"""
        if len(self.position_history) < 2:
            return False

        # Use the kinematic equation: s = ut + 0.5*a*t²
        # For constant acceleration motion

        dt = self.time_history[-1] - self.time_history[0]
        if dt <= 0:
            return False

        initial_pos = self.position_history[0]
        final_pos = self.position_history[-1]
        initial_vel = self.velocity_history[0]

        # Calculate expected displacement using kinematic equations
        # For now, we'll just check if the motion is consistent with basic physics
        dx = final_pos['x'] - initial_pos['x']
        dy = final_pos['y'] - initial_pos['y']
        dz = final_pos['z'] - initial_pos['z']

        # Calculate average velocity
        avg_vx = dx / dt if dt != 0 else 0
        avg_vy = dy / dt if dt != 0 else 0
        avg_vz = dz / dt if dt != 0 else 0

        # Compare with initial velocity to see if it's reasonable
        vel_change_x = abs(avg_vx - initial_vel['x'])
        vel_change_y = abs(avg_vy - initial_vel['y'])
        vel_change_z = abs(avg_vz - initial_vel['z'])

        # Allow for reasonable changes due to acceleration
        reasonable_change = (vel_change_x < 5.0 and
                           vel_change_y < 5.0 and
                           vel_change_z < 5.0)

        self.get_logger().info(f'Displacement: X={dx:.3f}, Y={dy:.3f}, Z={dz:.3f} m')
        self.get_logger().info(f'Average velocity: X={avg_vx:.3f}, Y={avg_vy:.3f}, Z={avg_vz:.3f} m/s')
        self.get_logger().info(f'Kinematic validation: {"PASS" if reasonable_change else "FAIL"}')

        return reasonable_change

    def validate_energy_conservation(self):
        """Validate that energy is conserved in closed systems (simplified)"""
        # This is a simplified check - in a real system, we'd check potential + kinetic energy
        # for conservation in a closed system without external forces

        if len(self.velocity_history) < 2:
            return False

        # Calculate kinetic energy (simplified - using mass of 1 for comparison)
        v1 = self.velocity_history[0]
        v2 = self.velocity_history[-1]

        ke1 = 0.5 * (v1['x']**2 + v1['y']**2 + v1['z']**2)
        ke2 = 0.5 * (v2['x']**2 + v2['y']**2 + v2['z']**2)

        # In a perfect system with no friction, KE should be conserved
        # In simulation, some energy loss is expected due to numerical integration
        energy_loss = abs(ke1 - ke2)

        # Allow up to 10% energy change as reasonable for simulation
        reasonable_energy_change = energy_loss < 0.1 * max(ke1, ke2, 1.0)

        self.get_logger().info(f'Kinetic energy: Start={ke1:.3f}, End={ke2:.3f}')
        self.get_logger().info(f'Energy change: {energy_loss:.3f}')
        self.get_logger().info(f'Energy conservation validation: {"PASS" if reasonable_energy_change else "FAIL"}')

        return reasonable_energy_change

    def run_validation_tests(self):
        """Run all real-world physics validation tests"""
        self.get_logger().info('Starting real-world physics validation tests...')

        # Wait a bit for data to accumulate
        time.sleep(3.0)

        results = {
            'gravity_validation': self.validate_gravity_acceleration(),
            'kinematic_validation': self.validate_kinematic_equations(),
            'energy_validation': self.validate_energy_conservation()
        }

        self.get_logger().info('Real-world physics validation results:')
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.get_logger().info(f'  {test_name}: {status}')

        all_passed = all(results.values())
        self.get_logger().info(f'Overall validation result: {"ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"}')

        return all_passed


def main(args=None):
    rclpy.init(args=args)

    validation_node = RealWorldPhysicsValidation()

    # Run the validation tests
    success = validation_node.run_validation_tests()

    # Shutdown
    validation_node.destroy_node()
    rclpy.shutdown()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()