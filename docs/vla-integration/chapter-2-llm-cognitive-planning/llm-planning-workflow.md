# LLM Planning Workflow

## Command Processing Flow

The LLM cognitive planning system processes natural language commands through several stages:

### 1. Command Reception
Commands arrive as `VLACommand` messages containing:
- `command_text`: The transcribed natural language command
- `confidence_score`: Confidence from the Whisper system
- `intent`: Inferred intent from text analysis
- `parameters`: Extracted parameters (objects, locations, etc.)

### 2. Intent Analysis
The system analyzes the command to determine the appropriate action category:
- **Navigation**: Movement-related commands
- **Manipulation**: Object interaction commands
- **Perception**: Detection and recognition commands
- **System**: Control and status commands

### 3. Action Sequence Generation
Based on the intent, the system generates a sequence of ROS 2 actions:

```
Input: "Pick up the red cup from the table"
Output: [
  {action_type: "PERCEPTION", parameters: ["object_type=red cup"]},
  {action_type: "NAVIGATION", parameters: ["object_type=red cup"]},
  {action_type: "MANIPULATION", parameters: ["object_type=red cup"]}
]
```

## Supported Action Types

### Navigation Actions
- **NAVIGATION**: Move the robot to a specific location or towards an object
  - Parameters: `location`, `object_id`, `approach_distance`
  - Example: `{location="kitchen"}`, `{object_id="red_cup_001", approach_distance=0.5}`

### Perception Actions
- **PERCEPTION**: Detect, recognize, or locate objects in the environment
  - Parameters: `object_types`, `detection_range`, `object_type`
  - Example: `{object_types=["cup", "ball"], detection_range=2.0}`

### Manipulation Actions
- **MANIPULATION**: Grasp, place, or manipulate objects
  - Parameters: `object_id`, `grasp_type`, `target_location`
  - Example: `{object_id="red_cup_001", grasp_type="top_grasp"}`

### System Actions
- **SYSTEM**: Wait, speak, or control system state
  - Parameters: `duration`, `text`, `command`
  - Example: `{duration=5.0}`, `{text="Task completed"}`

## LLM Integration

### API Configuration
The system supports multiple LLM providers:

#### OpenAI GPT
```yaml
llm_provider: "openai"
model_name: "gpt-4o"
api_key: "your-api-key-here"  # Set via environment variable recommended
```

#### Ollama (Local)
```yaml
llm_provider: "ollama"
model_name: "llama3"
ollama_host: "localhost"
ollama_port: 11434
```

### Prompt Engineering
The system uses carefully crafted prompts to ensure reliable action generation:

```python
prompt = f"""
Convert the following natural language command into a sequence of ROS 2 actions...

Available Action Types: NAVIGATION, PERCEPTION, MANIPULATION, SYSTEM
...
"""
```

## Safety Validation

All action sequences undergo safety validation before execution:

- **Environmental Safety**: Verify navigation targets exist and are accessible
- **Manipulation Safety**: Ensure objects can be safely grasped
- **System Safety**: Prevent actions that could harm the robot or environment

## Error Handling

The system handles various error conditions:

### LLM Communication Errors
- Retry with exponential backoff
- Fallback to predefined templates
- Graceful degradation to simple commands

### Invalid Action Sequences
- Parse error recovery
- Validation against known action types
- Request clarification for ambiguous commands

### Execution Failures
- Action dependency management
- Replanning when actions fail
- Safe stopping procedures

## Performance Considerations

### Response Time
- LLM calls typically take 1-10 seconds depending on model and complexity
- Caching for frequently used command patterns
- Asynchronous processing for non-critical commands

### Resource Usage
- API token consumption tracking
- Local model options for cost-sensitive applications
- Batch processing for multiple commands

## Testing and Validation

### Unit Testing
Test individual action generation functions:

```python
def test_navigation_command():
    generator = ActionGeneratorNode()
    sequence = generator._navigate_to_location("go to kitchen", [])
    assert len(sequence.actions) == 1
    assert sequence.actions[0].action_type == "NAVIGATION"
```

### Integration Testing
Test end-to-end command processing:

```bash
# Send a test command
ros2 topic pub /vla/command vla_interfaces/VLACommand "{
  command_text: 'pick up the red cup',
  confidence_score: 0.9,
  intent: 'PICK_UP_OBJECT',
  parameters: ['red', 'cup']
}"

# Monitor the generated action sequence
ros2 topic echo /vla/action_sequence
```

## Troubleshooting

### Poor LLM Responses
- Adjust temperature settings for more consistent outputs
- Refine prompts for better action formatting
- Use function calling capabilities if available

### Incorrect Action Sequences
- Verify intent classification accuracy
- Check parameter extraction logic
- Validate action templates against expected behaviors

### High API Costs
- Implement local models using Ollama
- Add response caching for common commands
- Optimize prompt length to reduce token usage

## Best Practices

### Command Design
- Use clear, unambiguous language
- Specify objects and locations explicitly
- Break complex tasks into simpler commands

### System Integration
- Monitor LLM response quality
- Implement fallback mechanisms
- Log and analyze failed commands for improvement