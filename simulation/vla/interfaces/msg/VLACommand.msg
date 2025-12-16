# VLA Command Message
# Message containing voice command processed by speech recognition

string command_text
float32 confidence_score
string intent
string[] parameters
builtin_interfaces/Time timestamp

# Example:
# command_text: "go to the kitchen"
# confidence_score: 0.92
# intent: "NAVIGATE_TO_LOCATION"
# parameters: ["kitchen"]
# timestamp: current time