#!/usr/bin/env python3

"""
URDF Parser example for ROS 2 fundamentals.

This node demonstrates how to parse and work with URDF (Unified Robot Description Format)
files in ROS 2. It shows how to load a URDF model and extract information about
links, joints, and other robot properties.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import xml.etree.ElementTree as ET
import os


class URDFParser(Node):
    """
    A node that demonstrates URDF parsing and robot model information extraction.
    """

    def __init__(self):
        # Initialize the node with the name 'urdf_parser'
        super().__init__('urdf_parser')

        # Create publisher for robot description (standard topic)
        self.robot_description_publisher = self.create_publisher(String, 'robot_description', 10)

        # Create publisher for parsed robot info
        self.robot_info_publisher = self.create_publisher(String, 'robot_info', 10)

        # URDF file path (parameter with default)
        self.declare_parameter('urdf_file', 'simulation/models/simple_humanoid/model.urdf')
        self.urdf_file = self.get_parameter('urdf_file').value

        # Timer to load and parse URDF periodically
        self.timer = self.create_timer(5.0, self.parse_urdf_callback)

        self.get_logger().info(f'URDF Parser initialized, loading: {self.urdf_file}')

    def parse_urdf_callback(self):
        """
        Timer callback to load and parse the URDF file.
        """
        try:
            # Check if URDF file exists
            if not os.path.exists(self.urdf_file):
                self.get_logger().error(f'URDF file not found: {self.urdf_file}')
                return

            # Read the URDF file
            with open(self.urdf_file, 'r') as file:
                urdf_content = file.read()

            # Publish the robot description (standard for visualization)
            robot_desc_msg = String()
            robot_desc_msg.data = urdf_content
            self.robot_description_publisher.publish(robot_desc_msg)

            # Parse the URDF XML
            root = ET.fromstring(urdf_content)

            # Extract robot information
            robot_name = root.get('name', 'unknown')
            links = root.findall('link')
            joints = root.findall('joint')

            # Create summary information
            info_text = f"Robot: {robot_name}, Links: {len(links)}, Joints: {len(joints)}"

            # Extract detailed information
            link_info = []
            for link in links:
                link_name = link.get('name', 'unnamed')
                visual = link.find('visual')
                collision = link.find('collision')
                inertial = link.find('inertial')

                link_details = f"Link '{link_name}':"
                if visual is not None:
                    link_details += " [visual]"
                if collision is not None:
                    link_details += " [collision]"
                if inertial is not None:
                    link_details += " [inertial]"

                link_info.append(link_details)

            joint_info = []
            for joint in joints:
                joint_name = joint.get('name', 'unnamed')
                joint_type = joint.get('type', 'unknown')
                parent = joint.find('parent')
                child = joint.find('child')

                parent_name = parent.get('link') if parent is not None else 'unknown'
                child_name = child.get('link') if child is not None else 'unknown'

                joint_details = f"Joint '{joint_name}' ({joint_type}): {parent_name} -> {child_name}"
                joint_info.append(joint_details)

            # Combine all information
            full_info = f"{info_text}\n\nLinks:\n" + "\n".join(link_info) + f"\n\nJoints:\n" + "\n".join(joint_info)

            # Publish detailed robot information
            info_msg = String()
            info_msg.data = full_info
            self.robot_info_publisher.publish(info_msg)

            self.get_logger().info(f'Parsed URDF: {info_text}')

        except ET.ParseError as e:
            self.get_logger().error(f'Error parsing URDF XML: {e}')
        except Exception as e:
            self.get_logger().error(f'Error loading URDF: {e}')

    def load_urdf_from_param_server(self):
        """
        Alternative method to load URDF from ROS parameter server.
        This is how URDF is typically loaded in real ROS systems.
        """
        try:
            self.declare_parameter('robot_description', descriptor=str)
            robot_description = self.get_parameter('robot_description').value

            if robot_description:
                root = ET.fromstring(robot_description)
                return root
            else:
                self.get_logger().warn('No robot_description parameter found')
                return None
        except Exception as e:
            self.get_logger().error(f'Error loading URDF from parameter server: {e}')
            return None

    def get_link_info(self, link_name):
        """
        Get information about a specific link.

        Args:
            link_name (str): Name of the link to query

        Returns:
            dict: Information about the link
        """
        try:
            with open(self.urdf_file, 'r') as file:
                urdf_content = file.read()
            root = ET.fromstring(urdf_content)

            link_element = root.find(f".//link[@name='{link_name}']")
            if link_element is None:
                return None

            link_info = {
                'name': link_name,
                'has_visual': link_element.find('visual') is not None,
                'has_collision': link_element.find('collision') is not None,
                'has_inertial': link_element.find('inertial') is not None
            }

            return link_info
        except Exception as e:
            self.get_logger().error(f'Error getting link info: {e}')
            return None

    def get_joint_info(self, joint_name):
        """
        Get information about a specific joint.

        Args:
            joint_name (str): Name of the joint to query

        Returns:
            dict: Information about the joint
        """
        try:
            with open(self.urdf_file, 'r') as file:
                urdf_content = file.read()
            root = ET.fromstring(urdf_content)

            joint_element = root.find(f".//joint[@name='{joint_name}']")
            if joint_element is None:
                return None

            parent_element = joint_element.find('parent')
            child_element = joint_element.find('child')

            joint_info = {
                'name': joint_name,
                'type': joint_element.get('type', 'unknown'),
                'parent': parent_element.get('link') if parent_element is not None else 'unknown',
                'child': child_element.get('link') if child_element is not None else 'unknown'
            }

            return joint_info
        except Exception as e:
            self.get_logger().error(f'Error getting joint info: {e}')
            return None


def main(args=None):
    """
    Main function that initializes the ROS 2 client library, creates the URDF parser node,
    and spins to keep the node running until interrupted.
    """
    # Initialize the ROS 2 client library
    rclpy.init(args=args)

    # Create an instance of the URDFParser
    urdf_parser = URDFParser()

    # Keep the node running until interrupted
    try:
        rclpy.spin(urdf_parser)
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly
    urdf_parser.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()