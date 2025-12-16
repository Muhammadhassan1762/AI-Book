# VLA Action Message
# Individual action within a sequence

string action_type  # NAVIGATION, PERCEPTION, MANIPULATION, SYSTEM
string[] action_parameters
int8 priority  # 0=LOW, 1=MEDIUM, 2=HIGH
builtin_interfaces/Duration timeout
string[] dependencies

# Constants for action types
string NAVIGATION = "NAVIGATION"
string PERCEPTION = "PERCEPTION"
string MANIPULATION = "MANIPULATION"
string SYSTEM = "SYSTEM"

# Constants for priority
int8 LOW = 0
int8 MEDIUM = 1
int8 HIGH = 2

# Example:
# action_type: "NAVIGATION"
# action_parameters: ["location=kitchen"]
# priority: 1
# timeout: duration(30.0)
# dependencies: []