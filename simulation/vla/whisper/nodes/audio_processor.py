#!/usr/bin/env python3
"""
Audio Processing Node for VLA System

This node handles audio input preprocessing before it's sent to the
Whisper speech-to-text system, including noise reduction and audio format conversion.
"""

import rclpy
from rclpy.node import Node
import numpy as np
from audio_common_msgs.msg import AudioData
from std_msgs.msg import Header
from vla_interfaces.msg import VLACommand
import scipy.signal as signal
from collections import deque
import threading


class AudioProcessorNode(Node):
    def __init__(self):
        super().__init__('audio_processor_node')

        # Declare parameters
        self.declare_parameter('sample_rate', 16000)
        self.declare_parameter('chunk_duration', 0.1)
        self.declare_parameter('silence_threshold', -50)
        self.declare_parameter('noise_reduction_enabled', True)
        self.declare_parameter('vad_enabled', True)  # Voice Activity Detection
        self.declare_parameter('input_audio_topic', '/hardware/microphone')
        self.declare_parameter('output_audio_topic', '/audio_input')
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')

        # Get parameters
        self.sample_rate = self.get_parameter('sample_rate').value
        self.chunk_duration = self.get_parameter('chunk_duration').value
        self.silence_threshold = self.get_parameter('silence_threshold').value
        self.noise_reduction_enabled = self.get_parameter('noise_reduction_enabled').value
        self.vad_enabled = self.get_parameter('vad_enabled').value
        input_audio_topic = self.get_parameter('input_audio_topic').value
        output_audio_topic = self.get_parameter('output_audio_topic').value
        self.enable_debug = self.get_parameter('enable_debug').value

        # Calculate chunk size
        self.chunk_size = int(self.sample_rate * self.chunk_duration)

        # Audio buffers and state
        self.audio_buffer = deque(maxlen=int(self.sample_rate * 2))  # 2 seconds buffer
        self.noise_floor = None
        self.is_listening = False

        # Create subscribers and publishers
        self.audio_sub = self.create_subscription(
            AudioData,
            input_audio_topic,
            self.audio_callback,
            10
        )

        self.processed_audio_pub = self.create_publisher(
            AudioData,
            output_audio_topic,
            10
        )

        # Timer for processing audio chunks
        self.process_timer = self.create_timer(self.chunk_duration, self.process_audio_chunk)

        self.get_logger().info('Audio Processor node initialized')

    def audio_callback(self, msg):
        """Callback for raw audio input"""
        try:
            # Convert audio data to numpy array (assuming 16-bit signed integers)
            audio_array = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32)

            # Add to buffer
            self.audio_buffer.extend(audio_array)

            # Update noise floor estimate if needed
            if self.noise_floor is None and len(self.audio_buffer) > 1000:
                self.estimate_noise_floor()

        except Exception as e:
            self.get_logger().error(f'Error processing audio input: {e}')

    def estimate_noise_floor(self):
        """Estimate the noise floor from the current audio buffer"""
        if len(self.audio_buffer) == 0:
            return

        # Convert buffer to numpy array
        audio_data = np.array(list(self.audio_buffer))

        # Calculate RMS of quiet periods (lowest 25% of values)
        rms_values = []
        chunk_size = 1024
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            if len(chunk) > 0:
                rms = np.sqrt(np.mean(chunk**2))
                rms_db = 20 * np.log10(max(rms, 1e-10))  # Avoid log(0)
                rms_values.append(rms_db)

        if rms_values:
            # Take the 25th percentile as noise floor
            self.noise_floor = np.percentile(rms_values, 25)
            self.get_logger().info(f'Estimated noise floor: {self.noise_floor:.2f} dB')

    def detect_voice_activity(self, audio_chunk):
        """Simple voice activity detection based on energy threshold"""
        if len(audio_chunk) == 0:
            return False

        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk**2))
        energy_db = 20 * np.log10(max(rms, 1e-10))

        # Voice activity if energy is above silence threshold
        # and significantly above noise floor (if available)
        if self.noise_floor is not None:
            return energy_db > self.silence_threshold and energy_db > (self.noise_floor + 10)
        else:
            return energy_db > self.silence_threshold

    def apply_noise_reduction(self, audio_chunk):
        """Apply basic noise reduction to audio chunk"""
        if not self.noise_reduction_enabled or len(audio_chunk) == 0:
            return audio_chunk

        try:
            # Simple spectral subtraction approach
            # Convert to frequency domain
            fft = np.fft.fft(audio_chunk)
            magnitude = np.abs(fft)
            phase = np.angle(fft)

            # Estimate noise spectrum (use a simple approach)
            if self.noise_floor is not None:
                noise_threshold = 10**(self.noise_floor / 20.0)  # Convert dB to linear
                # Apply spectral subtraction
                magnitude_reduced = np.maximum(magnitude - noise_threshold, 0)
            else:
                # Use a simple threshold based on silence_threshold
                noise_threshold = 10**(self.silence_threshold / 20.0)
                magnitude_reduced = np.maximum(magnitude - noise_threshold, 0)

            # Reconstruct signal
            fft_reduced = magnitude_reduced * np.exp(1j * phase)
            reduced_audio = np.real(np.fft.ifft(fft_reduced)).astype(np.float32)

            return reduced_audio
        except Exception as e:
            self.get_logger().warn(f'Noise reduction failed: {e}')
            return audio_chunk

    def process_audio_chunk(self):
        """Process a chunk of audio data"""
        if len(self.audio_buffer) < self.chunk_size:
            return  # Not enough data yet

        # Get audio chunk
        chunk_list = [self.audio_buffer.popleft() for _ in range(min(self.chunk_size, len(self.audio_buffer)))]
        audio_chunk = np.array(chunk_list, dtype=np.float32)

        # Apply noise reduction
        if self.noise_reduction_enabled:
            audio_chunk = self.apply_noise_reduction(audio_chunk)

        # Voice activity detection
        if self.vad_enabled:
            has_voice = self.detect_voice_activity(audio_chunk)
            if not has_voice:
                if self.is_listening:
                    self.get_logger().debug('Voice activity ended')
                    self.is_listening = False
                return  # Skip publishing if no voice detected
            else:
                if not self.is_listening:
                    self.get_logger().debug('Voice activity detected')
                    self.is_listening = True
        else:
            # If VAD is disabled, always publish audio
            has_voice = True

        # Convert back to int16 format for ROS message
        audio_int16 = (audio_chunk * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()

        # Create and publish AudioData message
        audio_msg = AudioData()
        audio_msg.data = audio_bytes

        self.processed_audio_pub.publish(audio_msg)

        if self.enable_debug:
            self.get_logger().debug(f'Published audio chunk of {len(audio_bytes)} bytes')

    def apply_bandpass_filter(self, audio_data, low_freq=300, high_freq=3400, sample_rate=16000):
        """Apply bandpass filter to audio data to remove out-of-band noise"""
        nyquist = sample_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist

        # Design Butterworth bandpass filter
        b, a = signal.butter(4, [low, high], btype='band', analog=False)

        # Apply filter (forward-backward to eliminate phase distortion)
        filtered_data = signal.filtfilt(b, a, audio_data)

        return filtered_data


def main(args=None):
    rclpy.init(args=args)
    node = AudioProcessorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()