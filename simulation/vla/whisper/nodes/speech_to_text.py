#!/usr/bin/env python3
"""
Whisper Speech-to-Text Node for VLA System

This node uses OpenAI Whisper to convert audio input to text commands
for the Vision-Language-Action pipeline.
"""

import rclpy
from rclpy.node import Node
import whisper
import torch
import numpy as np
from audio_common_msgs.msg import AudioData
from std_msgs.msg import String
from vla_interfaces.msg import VLACommand
from vla_interfaces.srv import ProcessCommand
import tempfile
import wave
import io


class SpeechToTextNode(Node):
    def __init__(self):
        super().__init__('whisper_node')

        # Declare parameters
        self.declare_parameter('model_size', 'base')
        self.declare_parameter('language', 'en')
        self.declare_parameter('use_gpu', True)
        self.declare_parameter('confidence_threshold', 0.7)
        self.declare_parameter('max_transcription_length', 200)
        self.declare_parameter('input_audio_topic', '/audio_input')
        self.declare_parameter('output_text_topic', '/vla/command')
        self.declare_parameter('process_command_service', '/vla/process_command')
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')

        # Get parameters
        self.model_size = self.get_parameter('model_size').value
        self.language = self.get_parameter('language').value
        self.use_gpu = self.get_parameter('use_gpu').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.max_transcription_length = self.get_parameter('max_transcription_length').value
        input_audio_topic = self.get_parameter('input_audio_topic').value
        output_text_topic = self.get_parameter('output_text_topic').value
        process_command_service = self.get_parameter('process_command_service').value
        self.enable_debug = self.get_parameter('enable_debug').value

        # Initialize Whisper model
        self.get_logger().info(f'Loading Whisper model: {self.model_size}')
        try:
            self.model = whisper.load_model(self.model_size, device='cuda' if self.use_gpu and torch.cuda.is_available() else 'cpu')
            self.get_logger().info('Whisper model loaded successfully')
        except Exception as e:
            self.get_logger().error(f'Failed to load Whisper model: {e}')
            raise

        # Create subscribers and publishers
        self.audio_sub = self.create_subscription(
            AudioData,
            input_audio_topic,
            self.audio_callback,
            10
        )

        self.command_pub = self.create_publisher(
            VLACommand,
            output_text_topic,
            10
        )

        # Create service server
        self.process_command_srv = self.create_service(
            ProcessCommand,
            process_command_service,
            self.process_command_callback
        )

        self.get_logger().info('Whisper Speech-to-Text node initialized')

    def audio_callback(self, msg):
        """Callback for audio input"""
        try:
            # Convert audio data to numpy array
            audio_array = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe audio using Whisper
            result = self.model.transcribe(audio_array, language=self.language)

            # Extract text and confidence
            text = result['text'].strip()
            if not text:
                self.get_logger().debug('No speech detected')
                return

            # Calculate confidence (using log probability as proxy)
            segments = result.get('segments', [])
            if segments:
                avg_logprob = np.mean([seg.get('avg_logprob', -1.0) for seg in segments])
                # Convert log probability to confidence score (0-1 range)
                confidence = max(0.0, min(1.0, (avg_logprob + 5) / 10))  # Normalize based on typical logprob range
            else:
                confidence = 0.5  # Default confidence if no segments

            if confidence < self.confidence_threshold:
                self.get_logger().warn(f'Transcription confidence {confidence:.2f} below threshold {self.confidence_threshold}')
                return

            if len(text) > self.max_transcription_length:
                self.get_logger().warn(f'Transcription length {len(text)} exceeds maximum {self.max_transcription_length}')
                text = text[:self.max_transcription_length]

            # Create and publish VLACommand message
            command_msg = VLACommand()
            command_msg.command_text = text
            command_msg.confidence_score = float(confidence)
            command_msg.intent = self.infer_intent(text)
            command_msg.parameters = self.extract_parameters(text)
            command_msg.timestamp = self.get_clock().now().to_msg()

            self.command_pub.publish(command_msg)
            self.get_logger().info(f'Transcribed: "{text}" (confidence: {confidence:.2f})')

        except Exception as e:
            self.get_logger().error(f'Error processing audio: {e}')

    def process_command_callback(self, request, response):
        """Service callback to process raw command"""
        try:
            # For this basic implementation, we just return the raw command
            # In a more advanced version, we could do additional processing
            response.success = True
            response.processed_command = request.raw_command
            response.intent = self.infer_intent(request.raw_command)
            response.parameters = self.extract_parameters(request.raw_command)
            response.error_message = ""
            response.error_code = 0

            # Check confidence threshold
            if request.audio_confidence < self.confidence_threshold:
                response.success = False
                response.error_message = f"Audio confidence {request.audio_confidence} below threshold {self.confidence_threshold}"
                response.error_code = 2  # Invalid input

        except Exception as e:
            response.success = False
            response.error_message = f"Error processing command: {e}"
            response.error_code = 1  # General error

        return response

    def infer_intent(self, text):
        """Simple intent inference based on keywords"""
        text_lower = text.lower()

        # Navigation intents
        if any(word in text_lower for word in ['go to', 'move to', 'navigate to', 'walk to', 'run to', 'go', 'move']):
            return 'NAVIGATE_TO_LOCATION'

        # Object manipulation intents
        if any(word in text_lower for word in ['pick up', 'grasp', 'take', 'grab', 'lift', 'hold', 'get', 'pick']):
            return 'PICK_UP_OBJECT'

        if any(word in text_lower for word in ['put down', 'place', 'set down', 'release', 'drop']):
            return 'PLACE_OBJECT'

        # Object detection intents
        if any(word in text_lower for word in ['find', 'locate', 'look for', 'search for', 'detect', 'see', 'spot']):
            return 'DETECT_OBJECTS'

        # General action intents
        if any(word in text_lower for word in ['clean', 'tidy', 'organize', 'arrange']):
            return 'CLEAN_ROOM'

        if any(word in text_lower for word in ['follow', 'come', 'follow me']):
            return 'FOLLOW_HUMAN'

        # Default intent
        return 'GENERAL_COMMAND'

    def extract_parameters(self, text):
        """Extract parameters from text command"""
        # Simple parameter extraction - in a real system, this would be more sophisticated
        words = text.lower().split()
        parameters = []

        # Look for location parameters
        location_keywords = ['kitchen', 'bedroom', 'living room', 'dining room', 'bathroom', 'office', 'table', 'chair']
        for word in words:
            if word in location_keywords:
                parameters.append(word)

        # Look for object parameters
        object_keywords = ['cup', 'bottle', 'book', 'ball', 'box', 'red', 'blue', 'green', 'cup', 'plate', 'fork']
        for word in words:
            if word in object_keywords:
                parameters.append(word)

        return parameters


def main(args=None):
    rclpy.init(args=args)
    node = SpeechToTextNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()