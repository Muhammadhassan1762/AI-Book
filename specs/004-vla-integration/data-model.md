# Data Model: Vision-Language-Action (VLA)

## Overview

This document defines the key data entities and their relationships for the Vision-Language-Action (VLA) system that connects speech recognition, language processing, and robotic action execution.

## Core Entities

### VoiceCommand

**Description**: Represents a natural language command received from speech recognition

**Attributes**:
- `id`: Unique identifier for the command
- `audio_data`: Raw audio input (optional, for debugging)
- `transcribed_text`: Text converted from speech
- `confidence_score`: Confidence level of speech recognition (0.0-1.0)
- `timestamp`: When the command was received
- `user_context`: Context about the user or environment (optional)
- `intent`: Parsed intent from the command
- `parameters`: Extracted parameters from the command

**Validation Rules**:
- `transcribed_text` must not be empty
- `confidence_score` must be between 0.0 and 1.0
- `timestamp` must be current or past time

**State Transitions**:
- `RECEIVED` → `PROCESSING` → `PLANNED` → `EXECUTING` → `COMPLETED` or `FAILED`

### ActionSequence

**Description**: Ordered list of ROS 2 actions generated from natural language command

**Attributes**:
- `id`: Unique identifier for the sequence
- `voice_command_id`: Reference to the originating voice command
- `actions`: List of Action objects in execution order
- `status`: Current status of the sequence (PENDING, EXECUTING, COMPLETED, FAILED)
- `created_at`: Timestamp when sequence was generated
- `estimated_duration`: Estimated time to complete all actions
- `safety_level`: Safety classification of the action sequence

**Validation Rules**:
- Must contain at least one action
- Actions must be in logical execution order
- All referenced services/actions must be available

### Action

**Description**: Individual ROS 2 action within an action sequence

**Attributes**:
- `id`: Unique identifier for the action
- `action_sequence_id`: Reference to the parent sequence
- `type`: Type of action (NAVIGATION, PERCEPTION, MANIPULATION, etc.)
- `parameters`: Parameters for the action execution
- `priority`: Execution priority (HIGH, MEDIUM, LOW)
- `timeout`: Maximum time allowed for execution
- `dependencies`: List of other actions this action depends on
- `status`: Current status (PENDING, EXECUTING, COMPLETED, FAILED)

**Validation Rules**:
- Type must be one of the defined action types
- Parameters must match the action type requirements
- Timeout must be positive

### TaskPlan

**Description**: Structured representation of robot objectives derived from voice commands

**Attributes**:
- `id`: Unique identifier for the plan
- `voice_command_id`: Reference to the originating voice command
- `action_sequence_id`: Reference to the generated action sequence
- `objectives`: List of high-level objectives
- `subtasks`: Breakdown of objectives into subtasks
- `constraints`: Constraints on task execution (safety, time, etc.)
- `success_criteria`: Criteria for task completion
- `fallback_procedures`: Procedures if primary tasks fail

**Validation Rules**:
- Must have at least one objective
- Subtasks must collectively satisfy all objectives
- Constraints must be feasible

### VLAContext

**Description**: Contextual information for the VLA pipeline execution

**Attributes**:
- `id`: Unique identifier for the context
- `current_location`: Robot's current location in the environment
- `environment_map`: Current map of the environment
- `detected_objects`: Objects currently detected in the environment
- `robot_capabilities`: Current capabilities of the robot
- `execution_history`: History of recent actions
- `safety_constraints`: Current safety constraints in effect

**Validation Rules**:
- Current location must be within the environment map
- Robot capabilities must be valid for the current configuration

## Relationships

```
VoiceCommand (1) → (1) TaskPlan
TaskPlan (1) → (1) ActionSequence
ActionSequence (1) → (*) Action
VLAContext (1) → (*) ActionSequence (executing sequences)
```

## Message Types for ROS 2 Integration

### VLACommand.msg

```
string command_text
float32 confidence_score
string intent
string[] parameters
time timestamp
```

### VLAAction.msg

```
string action_type
string[] action_parameters
int8 priority  # 0=LOW, 1=MEDIUM, 2=HIGH
duration timeout
string[] dependencies
```

### VLAActionSequence.msg

```
VLAAction[] actions
string status
duration estimated_duration
string safety_level
```

### VLAStatus.msg

```
string current_state
string current_action
float32 progress_percentage
string[] recent_actions
string error_message
```

## Validation and Constraints

### Data Integrity
- All timestamps must be properly formatted
- Confidence scores must be within 0.0-1.0 range
- Action parameters must match expected types for each action type

### Safety Constraints
- Actions requiring navigation must validate target locations exist in map
- Manipulation actions must verify object accessibility
- High-risk actions require additional validation steps

### Execution Constraints
- Action sequences must be executable within robot capabilities
- Dependencies must form a valid execution graph (no cycles)
- Resource conflicts between concurrent actions must be resolved