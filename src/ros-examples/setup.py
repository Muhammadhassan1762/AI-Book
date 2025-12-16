from setuptools import setup

package_name = 'ros2_fundamentals_examples'

setup(
    name=package_name,
    version='0.0.1',
    packages=[],
    py_modules=['basic_publisher', 'basic_subscriber', 'rclpy_template', 'ai_decision_node', 'robot_controller', 'urdf_parser'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='maintainer',
    maintainer_email='maintainer@todo.todo',
    description='Examples for ROS 2 fundamentals module',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'basic_publisher = basic_publisher:main',
            'basic_subscriber = basic_subscriber:main',
            'ai_decision_node = ai_decision_node:main',
            'robot_controller = robot_controller:main',
            'urdf_parser = urdf_parser:main',
        ],
    },
)