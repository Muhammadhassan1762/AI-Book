#!/usr/bin/env python3
"""
Whisper Testing Script for VLA System

This script tests the Whisper speech-to-text functionality by simulating
audio input and verifying the transcription output.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import numpy as np
import time
import threading
from audio_common_msgs.msg import AudioData
from vla_interfaces.msg import VLACommand
from vla_interfaces.srv import ProcessCommand


class WhisperTester(Node):
    def __init__(self):
        super().__init__('whisper_tester')

        # Create publisher for simulated audio data
        self.audio_pub = self.create_publisher(
            AudioData,
            '/audio_input',
            10
        )

        # Create subscriber to listen for VLA commands
        self.command_sub = self.create_subscription(
            VLACommand,
            '/vla/command',
            self.command_callback,
            10
        )

        # Create client for process command service
        self.process_command_client = self.create_client(
            ProcessCommand,
            '/vla/process_command'
        )

        # Wait for service to be available
        while not self.process_command_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Process command service not available, waiting...')

        # Test results
        self.last_command = None
        self.test_results = []

        self.get_logger().info('Whisper tester initialized')

    def command_callback(self, msg):
        """Callback for received VLA commands"""
        self.last_command = msg
        self.get_logger().info(f'Received command: "{msg.command_text}" (confidence: {msg.confidence_score:.2f})')

    def create_test_audio(self, text="hello world", sample_rate=16000):
        """
        Create synthetic audio data for testing (simplified simulation).
        In a real test, you would use actual audio files or recording.
        """
        # For testing purposes, we'll create a placeholder audio buffer
        # In practice, you would use real audio data or audio synthesis
        duration = len(text) * 0.1  # Rough estimate of duration
        num_samples = int(sample_rate * duration)

        # Create a simple waveform (this is just for testing - not real audio synthesis)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        # Create a combination of sine waves to simulate speech-like sounds
        audio_data = np.sin(2 * np.pi * 440 * t) * 0.3  # A note
        audio_data += np.sin(2 * np.pi * 880 * t) * 0.2  # Higher harmonic
        audio_data += np.random.normal(0, 0.1, num_samples)  # Add some noise

        # Convert to int16 and then to bytes
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()

        return audio_bytes

    def test_audio_processing(self):
        """Test audio processing by publishing test audio and checking for commands"""
        self.get_logger().info('Starting audio processing test...')

        # Create test audio data
        test_text = "move to the kitchen"
        audio_data = self.create_test_audio(test_text)

        # Publish audio data
        audio_msg = AudioData()
        audio_msg.data = audio_data
        self.audio_pub.publish(audio_msg)

        self.get_logger().info(f'Published test audio for: "{test_text}"')

        # Wait to receive response
        time.sleep(2.0)

        if self.last_command:
            self.get_logger().info(f'Test passed: Received command "{self.last_command.command_text}"')
            return True
        else:
            self.get_logger().warn('Test failed: No command received')
            return False

    def test_service_call(self):
        """Test the process command service"""
        self.get_logger().info('Testing process command service...')

        # Create request
        request = ProcessCommand.Request()
        request.raw_command = "pick up the red cup"
        request.audio_confidence = 0.9

        # Make service call
        future = self.process_command_client.call_async(request)

        # Wait for response
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(f'Service response: success={response.success}, intent={response.intent}')

            if response.success:
                self.get_logger().info('Service test passed')
                return True
            else:
                self.get_logger().warn(f'Service test failed: {response.error_message}')
                return False
        else:
            self.get_logger().warn('Service call failed or timed out')
            return False

    def run_all_tests(self):
        """Run all whisper tests"""
        self.get_logger().info('Starting Whisper system tests...')

        results = []

        # Test 1: Audio processing
        self.get_logger().info('Test 1: Audio Processing')
        result1 = self.test_audio_processing()
        results.append(('Audio Processing', result1))

        # Wait a bit between tests
        time.sleep(1.0)

        # Test 2: Service call
        self.get_logger().info('Test 2: Service Call')
        result2 = self.test_service_call()
        results.append(('Service Call', result2))

        # Wait a bit more
        time.sleep(1.0)

        # Test 3: Multiple commands
        self.get_logger().info('Test 3: Multiple Commands')
        commands_to_test = [
            "go to the kitchen",
            "pick up the blue ball",
            "find the red cup"
        ]

        all_passed = True
        for cmd in commands_to_test:
            self.get_logger().info(f'Testing command: "{cmd}"')
            request = ProcessCommand.Request()
            request.raw_command = cmd
            request.audio_confidence = 0.85

            future = self.process_command_client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

            if future.result() is not None and future.result().success:
                self.get_logger().info(f'Command "{cmd}" processed successfully')
            else:
                self.get_logger().warn(f'Command "{cmd}" failed')
                all_passed = False

        results.append(('Multiple Commands', all_passed))

        # Print summary
        self.get_logger().info('\n=== Test Results Summary ===')
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

    tester = WhisperTester()

    # Use a multi-threaded executor to handle callbacks while running tests
    executor = MultiThreadedExecutor()
    executor.add_node(tester)

    try:
        # Run all tests in a separate thread to allow callbacks to process
        test_thread = threading.Thread(target=lambda: tester.run_all_tests())
        test_thread.start()

        # Spin to handle callbacks
        executor.spin()

        test_thread.join()
    except KeyboardInterrupt:
        tester.get_logger().info('Test interrupted by user')
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()