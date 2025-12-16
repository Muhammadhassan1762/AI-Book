# VLA Integration Quickstart Guide

## Overview

This quickstart guide will help you get up and running with the Vision-Language-Action (VLA) system quickly. The VLA system enables voice-command-to-action execution for humanoid robots using Whisper for speech recognition, LLMs for cognitive planning, and ROS 2 for action execution.

## Prerequisites

Before starting, ensure you have:

- ROS 2 Humble Hawksbill installed
- Python 3.8+ with pip
- OpenAI API key (or Ollama for local LLM)
- Audio input device (microphone)
- Basic understanding of ROS 2 concepts

## Installation

### 1. Install Dependencies

```bash
pip install openai-whisper
pip install torch
pip install numpy
pip install scipy
pip install openai
```

### 2. Install ROS 2 Audio Packages

```bash
sudo apt-get install ros-humble-audio-common-msgs
```

## Quick Setup

### 1. Launch the Complete VLA System

Start the entire VLA pipeline with one command:

```bash
ros2 launch vla_integration vla_integration.launch.py
```

This launches:
- Whisper speech-to-text components
- LLM cognitive planning components
- VLA integration pipeline
- Safety validation system
- Context management

### 2. Test Voice Commands

Open a new terminal and test a simple command:

```bash
# Send a simple navigation command
ros2 topic pub /vla/command vla_interfaces/VLACommand "{
  command_text: 'go to the kitchen',
  confidence_score: 0.9,
  intent: 'NAVIGATE_TO_LOCATION',
  parameters: ['kitchen']
}"
```

Monitor the status:
```bash
ros2 topic echo /vla/status
```

## Basic Voice Commands

### Navigation Commands
```bash
# Navigate to location
ros2 topic pub /vla/command vla_interfaces/VLACommand "{
  command_text: 'go to the bedroom',
  confidence_score: 0.85,
  intent: 'NAVIGATE_TO_LOCATION',
  parameters: ['bedroom']
}"
```

### Manipulation Commands
```bash
# Pick up object
ros2 topic pub /vla/command vla_interfaces/VLACommand "{
  command_text: 'pick up the red cup',
  confidence_score: 0.9,
  intent: 'PICK_UP_OBJECT',
  parameters: ['red', 'cup']
}"
```

### Complex Commands
```bash
# Multi-step command
ros2 topic pub /vla/command vla_interfaces/VLACommand "{
  command_text: 'find the blue ball and bring it to me',
  confidence_score: 0.8,
  intent: 'FIND_AND_BRING',
  parameters: ['blue', 'ball']
}"
```

## Service-Based Execution

You can also use the pipeline service for direct execution:

```bash
ros2 service call /vla/execute_pipeline vla_interfaces/srv/ProcessCommand "{
  raw_command: 'move to the office',
  audio_confidence: 0.85
}"
```

## Monitoring the Pipeline

Monitor different aspects of the pipeline:

```bash
# Monitor pipeline status
ros2 topic echo /vla/status

# Monitor generated action sequences
ros2 topic echo /vla/action_sequence

# Monitor errors
ros2 topic echo /vla/error
```

## Configuration

### Whisper Configuration
Edit `simulation/vla/whisper/config/whisper_config.yaml` to adjust:

- Model size (tiny, base, small, medium, large)
- Language settings
- Confidence thresholds
- Audio processing parameters

### LLM Configuration
Edit `simulation/vla/llm_planner/config/llm_config.yaml` to adjust:

- LLM provider (OpenAI, Ollama)
- Model selection
- API keys and endpoints
- Planning parameters

### Integration Configuration
Edit `simulation/vla/integration/config/vla_config.yaml` to adjust:

- Pipeline behavior
- Safety validation settings
- Timeout values
- Performance monitoring

## Example Workflows

### 1. Simple Navigation
1. Launch the system: `ros2 launch vla_integration vla_integration.launch.py`
2. Send command: Navigate to kitchen
3. Monitor: Check status and action sequence
4. Observe: Robot moves to kitchen

### 2. Object Manipulation
1. Launch the system
2. Send command: "Pick up the red cup"
3. System will: Detect → Navigate → Grasp
4. Monitor progress via status topic

### 3. Complex Task Execution
1. Launch the system
2. Send command: "Clean the room"
3. System will: Plan multi-step action sequence
4. Execute: Perception → Navigation → Manipulation actions

## Troubleshooting

### Common Issues

**No Audio Input**
- Check microphone permissions
- Verify audio input device is working
- Check sample rate configuration

**Poor Speech Recognition**
- Ensure quiet environment
- Try different Whisper model sizes
- Check language setting

**LLM Not Responding**
- Verify API key is set
- Check network connectivity
- Try local Ollama as alternative

**Safety Validation Failing**
- Check configuration settings
- Verify target locations are safe
- Review action parameters

### Debugging Commands

Enable debug logging:
```bash
# Set log level to debug
export RCUTILS_LOGGING_SEVERITY_THRESHOLD=DEBUG
```

Check all VLA topics:
```bash
ros2 topic list | grep vla
```

## Next Steps

After completing this quickstart:

1. Explore detailed documentation for each component:
   - Chapter 1: Whisper Voice Input
   - Chapter 2: LLM Cognitive Planning
   - Chapter 3: VLA Pipeline Integration

2. Try more complex commands and scenarios

3. Customize configurations for your specific use case

4. Implement safety and validation for your environment

5. Extend with custom action types and capabilities

## Resources

- [Chapter 1: Whisper Voice Input](./chapter-1-whisper-voice-input/index.md) - Detailed Whisper setup and configuration
- [Chapter 2: LLM Cognitive Planning](./chapter-2-llm-cognitive-planning/index.md) - LLM planning and action generation
- [Chapter 3: VLA Pipeline Integration](./chapter-3-vla-pipeline-integration/index.md) - Complete system integration
- [API Reference](./api-reference.md) - Complete message and service definitions
- [Troubleshooting Guide](./troubleshooting.md) - Common issues and solutions