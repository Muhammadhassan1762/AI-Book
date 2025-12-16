# VLA Status Message
# Status updates for VLA pipeline execution

string current_state  # IDLE, LISTENING, PROCESSING, PLANNING, EXECUTING, COMPLETED, ERROR
string current_action
float32 progress_percentage
string[] recent_actions
string error_message
builtin_interfaces/Time timestamp

# Constants for current state
string IDLE = "IDLE"
string LISTENING = "LISTENING"
string PROCESSING = "PROCESSING"
string PLANNING = "PLANNING"
string EXECUTING = "EXECUTING"
string COMPLETED = "COMPLETED"
string ERROR = "ERROR"

# Example:
# current_state: "EXECUTING"
# current_action: "NAVIGATING_TO_LOCATION"
# progress_percentage: 65.0
# recent_actions: ["RECEIVED_COMMAND", "GENERATED_PLAN"]
# error_message: ""
# timestamp: current time