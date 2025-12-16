# Whisper Setup and Usage

## Installation and Dependencies

To use Whisper for voice input processing in your VLA system, you'll need to install the required dependencies:

```bash
pip install openai-whisper
pip install torch
pip install numpy
pip install scipy
```

Additionally, you'll need ROS 2 audio packages:

```bash
sudo apt-get install ros-humble-audio-common-msgs
```

## Configuration

The Whisper system is configured through the `whisper_config.yaml` file. Key parameters include:

- `model_size`: Whisper model to use (tiny, base, small, medium, large)
- `language`: Language code for speech recognition (en, es, fr, etc.)
- `use_gpu`: Whether to use GPU acceleration
- `confidence_threshold`: Minimum confidence for accepted transcription
- `sample_rate`: Audio sample rate in Hz (typically 16000)

## Launching the System

To start the Whisper voice input system, use the provided launch file:

```bash
ros2 launch vla_whisper whisper_pipeline.launch.py
```

This will start both the audio processor and speech-to-text nodes.

## Testing Voice Commands

To test the system, you can use the audio input topic directly:

```bash
# Listen to the VLA command output
ros2 topic echo /vla/command

# Or use the process command service
ros2 service call /vla/process_command vla_interfaces/srv/ProcessCommand "{
  raw_command: 'move to the kitchen',
  audio_confidence: 0.9
}"
```

## Audio Preprocessing

The audio processor node performs several important preprocessing steps:

### Noise Reduction
The system applies spectral subtraction to reduce background noise, improving transcription accuracy in noisy environments.

### Voice Activity Detection (VAD)
Voice activity detection identifies when someone is speaking, reducing unnecessary processing of silent periods.

### Bandpass Filtering
A bandpass filter removes frequencies outside the human speech range (typically 300Hz-3400Hz), reducing interference.

## Understanding Confidence Scores

Whisper provides confidence scores that indicate the reliability of transcriptions:

- **High Confidence (0.8-1.0)**: Accurate transcription expected
- **Medium Confidence (0.6-0.8)**: Transcription likely accurate but verify
- **Low Confidence (0.0-0.6)**: Transcription may be incorrect

The system filters out transcriptions below the configured confidence threshold to avoid acting on incorrect commands.

## Common Voice Commands

The system recognizes various command patterns:

### Navigation Commands
- "Go to the kitchen"
- "Move to the table"
- "Navigate to the bedroom"

### Object Manipulation Commands
- "Pick up the red cup"
- "Grasp the blue ball"
- "Take the book from the shelf"

### Detection Commands
- "Find the cup"
- "Locate the ball"
- "Look for the red object"

## Troubleshooting

### Poor Recognition Quality
- Ensure your microphone is positioned correctly
- Check for background noise interference
- Verify the language setting matches the spoken language
- Try different Whisper model sizes for better accuracy

### No Audio Detected
- Verify microphone permissions and connections
- Check that the audio input topic is publishing data
- Ensure the sample rate matches your audio source

### High CPU Usage
- Use smaller Whisper models (tiny or base) for real-time performance
- Reduce the audio processing frequency
- Consider using GPU acceleration if available

## Integration with VLA System

The Whisper system outputs `VLACommand` messages that are consumed by the LLM planner component. These messages contain:

- The transcribed text command
- Confidence score
- Inferred intent
- Extracted parameters
- Timestamp

This allows the LLM planner to convert natural language commands into executable ROS 2 action sequences.