# Chapter 2: LLM Cognitive Planning

## Overview

Welcome to Chapter 2 of the Vision-Language-Action (VLA) integration guide! In this chapter, we'll explore how Large Language Models (LLMs) enable cognitive planning for humanoid robots. This forms the reasoning component of our perception → reasoning → action pipeline, where natural language commands are transformed into executable action sequences.

## Learning Objectives

By the end of this chapter, you will:

- Understand how LLMs process natural language commands for robotic tasks
- Set up and configure the LLM cognitive planning pipeline
- Convert high-level commands to detailed action sequences
- Implement safety validation for planned actions
- Integrate LLM planning with the broader VLA system

## The Cognitive Planning Pipeline

The cognitive planning pipeline is the "brain" of our VLA system, bridging human language understanding with robotic action execution. When a user issues a command like "clean the room", the following sequence occurs:

1. **Command Input**: Natural language command received from Whisper system
2. **Intent Analysis**: LLM interprets the command's meaning and goal
3. **Action Planning**: LLM generates a sequence of specific robot actions
4. **Safety Validation**: Action sequence is checked for safety compliance
5. **Execution Preparation**: Action sequence is formatted for ROS 2 execution

## Architecture Overview

The LLM cognitive planning system consists of two main nodes:

- **Cognitive Planner Node**: Uses LLM to convert natural language to action sequences
- **Action Generator Node**: Specializes in creating detailed action sequences based on intent
- **Command Mapper Node**: Maps natural language commands to appropriate action sequences

```
┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│ VLA Command  │───▶│ Cognitive       │───▶│ Action          │───▶│ VLA Action          │
│              │    │ Planner         │    │ Generator       │    │ Sequence            │
│              │    │ (LLM Processing)│    │ (Action Details)│    │                     │
└──────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────────┘
         │                   │                       │                       │
         └───────────────────┼───────────────────────┼───────────────────────┘
                             ▼                       ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │ Command         │───▶│ Safety          │
                    │ Mapper          │    │ Validation      │
                    │ (Intent Mapping)│    │ (Action Safety) │
                    └─────────────────┘    └─────────────────┘
```

### Processing Flow

1. VLACommand received with text, intent, and parameters
2. Cognitive Planner uses LLM to generate high-level action plan
3. Action Generator creates detailed action sequence with parameters
4. Command Mapper refines action mapping and dependencies
5. Safety Validation checks action sequence before execution
6. VLAActionSequence published for execution

## Supported Command Types

The system handles various command categories:

- **Navigation Commands**: "Go to the kitchen", "Move to the table"
- **Manipulation Commands**: "Pick up the red cup", "Place the book on the shelf"
- **Perception Commands**: "Find the ball", "Detect all cups in the room"
- **Complex Multi-step Commands**: "Clean the room", "Organize the desk"

## Prerequisites

Before starting this chapter, ensure you have:

- Completed Chapter 1 (Whisper Voice Input)
- Access to an LLM API (OpenAI GPT or Ollama)
- Understanding of ROS 2 action concepts
- Basic knowledge of natural language processing

## Cross-References

- [Chapter 1: Whisper Voice Input](../chapter-1-whisper-voice-input/index.md) - Voice command processing that feeds into LLM planning
- [Chapter 3: VLA Pipeline Integration](../chapter-3-vla-pipeline-integration/index.md) - Complete pipeline that includes LLM planning
- [Quickstart Guide](../quickstart.md) - Quick setup and basic usage examples
- [API Reference](../api-reference.md) - Message and service definitions used in planning

## Next Steps

In the next section, we'll cover the detailed workflow of how LLMs transform natural language commands into executable robot actions.