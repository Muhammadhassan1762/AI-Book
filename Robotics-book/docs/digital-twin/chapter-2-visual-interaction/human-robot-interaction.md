---
sidebar_position: 3
---

# Human-Robot Interaction

## Creating Realistic Interaction Scenarios in Unity

Human-robot interaction (HRI) simulation is crucial for developing and testing vision-language-action systems. Unity provides the tools to create realistic interaction scenarios where humans can communicate with humanoid robots through voice commands, gestures, and visual cues in photorealistic environments.

## Learning Objectives

By the end of this chapter, you will:
- Design realistic human-robot interaction scenarios in Unity
- Implement voice command simulation with realistic acoustic properties
- Create gesture recognition and response systems
- Develop multimodal interaction interfaces
- Validate HRI systems in simulation before physical deployment

## Interaction Scenario Design

### Realistic Home Environment Setup

```csharp
using UnityEngine;
using System.Collections.Generic;

public class HomeEnvironmentSetup : MonoBehaviour
{
    [Header("Room Configuration")]
    public Transform kitchenArea;
    public Transform livingRoomArea;
    public Transform bedroomArea;

    [Header("Interactive Objects")]
    public GameObject[] kitchenObjects;  // cups, plates, etc.
    public GameObject[] livingRoomObjects;  // books, remote, etc.
    public GameObject[] bedroomObjects;  // clothes, etc.

    [Header("Human Placement")]
    public Transform[] humanSpawnPoints;
    public Transform[] robotSpawnPoints;

    void Start()
    {
        SetupInteractiveEnvironment();
        PlaceInteractiveObjects();
        ConfigureAcousticProperties();
    }

    void SetupInteractiveEnvironment()
    {
        // Configure each room with appropriate interactive elements
        ConfigureKitchen();
        ConfigureLivingRoom();
        ConfigureBedroom();
    }

    void ConfigureKitchen()
    {
        // Place kitchen-specific objects
        foreach (GameObject obj in kitchenObjects)
        {
            Vector3 randomPos = kitchenArea.position + new Vector3(
                Random.Range(-2f, 2f),
                0,
                Random.Range(-1.5f, 1.5f)
            );

            GameObject instance = Instantiate(obj, randomPos, Quaternion.identity);
            instance.transform.SetParent(kitchenArea);

            // Add interaction components
            AddInteractionComponent(instance);
        }
    }

    void ConfigureLivingRoom()
    {
        // Place living room objects
        foreach (GameObject obj in livingRoomObjects)
        {
            Vector3 randomPos = livingRoomArea.position + new Vector3(
                Random.Range(-3f, 3f),
                0,
                Random.Range(-2f, 2f)
            );

            GameObject instance = Instantiate(obj, randomPos, Quaternion.identity);
            instance.transform.SetParent(livingRoomArea);

            AddInteractionComponent(instance);
        }
    }

    void ConfigureBedroom()
    {
        // Place bedroom objects
        foreach (GameObject obj in bedroomObjects)
        {
            Vector3 randomPos = bedroomArea.position + new Vector3(
                Random.Range(-2f, 2f),
                0,
                Random.Range(-2f, 2f)
            );

            GameObject instance = Instantiate(obj, randomPos, Quaternion.identity);
            instance.transform.SetParent(bedroomArea);

            AddInteractionComponent(instance);
        }
    }

    void AddInteractionComponent(GameObject obj)
    {
        // Add interaction capabilities to objects
        var interaction = obj.AddComponent<InteractiveObject>();
        interaction.objectName = obj.name;
        interaction.objectType = GetObjectType(obj.name);
    }

    ObjectType GetObjectType(string name)
    {
        string lowerName = name.ToLower();
        if (lowerName.Contains("cup") || lowerName.Contains("glass"))
            return ObjectType.Drinkware;
        else if (lowerName.Contains("book") || lowerName.Contains("magazine"))
            return ObjectType.ReadingMaterial;
        else if (lowerName.Contains("remote"))
            return ObjectType.Electronics;
        else
            return ObjectType.Miscellaneous;
    }

    void ConfigureAcousticProperties()
    {
        // Set up acoustic zones for realistic sound propagation
        var kitchenAcoustic = kitchenArea.gameObject.AddComponent<AcousticZone>();
        kitchenAcoustic.zoneType = AcousticZone.ZoneType.Room;
        kitchenAcoustic.reverbLevel = 0.3f;

        var livingRoomAcoustic = livingRoomArea.gameObject.AddComponent<AcousticZone>();
        livingRoomAcoustic.zoneType = AcousticZone.ZoneType.Room;
        livingRoomAcoustic.reverbLevel = 0.5f;

        var bedroomAcoustic = bedroomArea.gameObject.AddComponent<AcousticZone>();
        bedroomAcoustic.zoneType = AcousticZone.ZoneType.Room;
        bedroomAcoustic.reverbLevel = 0.2f;
    }
}

public enum ObjectType
{
    Drinkware,
    ReadingMaterial,
    Electronics,
    Clothing,
    Food,
    Miscellaneous
}

public class AcousticZone : MonoBehaviour
{
    public enum ZoneType { Room, Hallway, OpenSpace }
    public ZoneType zoneType;
    [Range(0, 1)] public float reverbLevel = 0.5f;
    [Range(0, 1)] public float echoLevel = 0.3f;
}
```

## Voice Command Simulation

### Acoustic Environment Simulation

```csharp
using UnityEngine;
using UnityEngine.Audio;
using System.Collections;

public class VoiceCommandSimulator : MonoBehaviour
{
    [Header("Audio Configuration")]
    public AudioSource humanVoiceSource;
    public AudioSource robotVoiceSource;
    public AudioMixerGroup voiceMixerGroup;

    [Header("Acoustic Properties")]
    public float voiceVolume = 1.0f;
    public float noiseLevel = 0.1f;
    public float reverbLevel = 0.3f;

    [Header("Command Processing")]
    public float commandDelay = 0.5f; // Processing delay
    public float confidenceThreshold = 0.7f;

    private ROS2UnityComponent ros2Unity;
    private Publisher commandPublisher;
    private Subscriber commandResponseSubscriber;

    void Start()
    {
        InitializeAudioSystem();
        InitializeROSConnection();
    }

    void InitializeAudioSystem()
    {
        // Configure human voice source
        humanVoiceSource.outputAudioMixerGroup = voiceMixerGroup;
        humanVoiceSource.volume = voiceVolume;

        // Configure robot voice source
        robotVoiceSource.outputAudioMixerGroup = voiceMixerGroup;
        robotVoiceSource.volume = voiceVolume;
    }

    void InitializeROSConnection()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        commandPublisher = ros2Unity.CreatePublisher<std_msgs.msg.String>("vla_commands");
        commandResponseSubscriber = ros2Unity.CreateSubscriber<std_msgs.msg.String>(
            "vla_responses", CommandResponseCallback
        );
    }

    public void SimulateVoiceCommand(string command, Vector3 sourcePosition)
    {
        // Apply acoustic effects based on environment
        string processedCommand = ApplyAcousticEffects(command, sourcePosition);

        // Publish to ROS 2 with simulated confidence
        var commandMsg = new std_msgs.msg.String();
        commandMsg.data = processedCommand;

        commandPublisher.Publish(commandMsg);

        // Simulate processing delay
        StartCoroutine(SimulateProcessingDelay(command));
    }

    string ApplyAcousticEffects(string command, Vector3 sourcePosition)
    {
        // Simulate environmental effects
        string processedCommand = command;

        // Add noise based on distance and environment
        float noiseFactor = CalculateNoiseFactor(sourcePosition);
        if (Random.value < noiseFactor)
        {
            processedCommand = AddSimulatedNoise(processedCommand);
        }

        // Add delay based on distance
        float distanceFactor = Vector3.Distance(sourcePosition, transform.position);
        float delay = commandDelay + (distanceFactor * 0.01f); // 10ms per meter

        return processedCommand;
    }

    float CalculateNoiseFactor(Vector3 sourcePosition)
    {
        // Calculate noise based on environment and distance
        float baseNoise = noiseLevel;

        // Check which acoustic zone we're in
        AcousticZone zone = GetAcousticZone(sourcePosition);
        if (zone != null)
        {
            baseNoise *= (1 + zone.reverbLevel);
        }

        // Distance affects clarity
        float distance = Vector3.Distance(sourcePosition, transform.position);
        baseNoise += Mathf.Clamp01(distance / 10.0f) * 0.3f; // 30% max additional noise

        return baseNoise;
    }

    AcousticZone GetAcousticZone(Vector3 position)
    {
        // Find the acoustic zone containing this position
        AcousticZone[] zones = FindObjectsOfType<AcousticZone>();
        foreach (var zone in zones)
        {
            // Simple distance check - in real implementation, use bounds or triggers
            if (Vector3.Distance(position, zone.transform.position) < 5f)
            {
                return zone;
            }
        }
        return null;
    }

    string AddSimulatedNoise(string command)
    {
        // Add realistic speech recognition errors
        string[] noiseWords = { "um", "uh", "er", "" }; // Pauses and filler words
        string[] similarWords = { "kitchen", "chicken", "bedroom", "bathroom" }; // Similar sounding

        string[] words = command.Split(' ');
        for (int i = 0; i < words.Length; i++)
        {
            if (Random.value < 0.1f) // 10% chance of noise
            {
                string noiseWord = noiseWords[Random.Range(0, noiseWords.Length)];
                if (!string.IsNullOrEmpty(noiseWord))
                {
                    words[i] = noiseWord + " " + words[i];
                }
            }
        }

        return string.Join(" ", words);
    }

    IEnumerator SimulateProcessingDelay(string originalCommand)
    {
        yield return new WaitForSeconds(commandDelay);

        // Simulate response
        string response = GenerateSimulatedResponse(originalCommand);
        SimulateRobotResponse(response);
    }

    string GenerateSimulatedResponse(string command)
    {
        // Generate appropriate response based on command
        if (command.ToLower().Contains("clean"))
        {
            return "I will start cleaning the room now.";
        }
        else if (command.ToLower().Contains("go to") || command.ToLower().Contains("move to"))
        {
            return "I am navigating to the requested location.";
        }
        else if (command.ToLower().Contains("pick up") || command.ToLower().Contains("grasp"))
        {
            return "I will pick up the requested object.";
        }
        else
        {
            return "I received your command and will process it.";
        }
    }

    void SimulateRobotResponse(string response)
    {
        // Play robot voice response
        robotVoiceSource.PlayOneShot(CreateResponseAudio(response));

        // Publish response to ROS 2
        var responseMsg = new std_msgs.msg.String();
        responseMsg.data = response;
        // Publisher would be available here
    }

    AudioClip CreateResponseAudio(string text)
    {
        // In a real implementation, this would use text-to-speech
        // For simulation, we'll create a placeholder
        return null;
    }

    void CommandResponseCallback(std_msgs.msg.String msg)
    {
        // Handle actual ROS 2 responses
        Debug.Log($"Robot response: {msg.data}");
    }
}
```

## Gesture Recognition and Response

### Visual Gesture Detection

```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public class GestureRecognitionSystem : MonoBehaviour
{
    [Header("Gesture Detection")]
    public Camera gestureDetectionCamera;
    public RawImage gestureVisualization;
    public float gestureDetectionRadius = 0.5f;

    [Header("Gesture Mapping")]
    public GestureCommand[] gestureCommands;

    [Header("Human Tracking")]
    public Transform humanTransform;
    public Transform robotTransform;

    private Dictionary<string, GestureCommand> gestureMap;
    private List<Vector3> handPositions = new List<Vector3>();
    private float gestureTimeout = 3.0f;
    private float gestureTimer = 0f;

    void Start()
    {
        InitializeGestureSystem();
    }

    void InitializeGestureSystem()
    {
        // Create gesture mapping
        gestureMap = new Dictionary<string, GestureCommand>();
        foreach (var gesture in gestureCommands)
        {
            gestureMap[gesture.gestureName] = gesture;
        }
    }

    void Update()
    {
        DetectAndProcessGestures();
    }

    void DetectAndProcessGestures()
    {
        // Simulate gesture detection
        if (humanTransform != null && robotTransform != null)
        {
            float distance = Vector3.Distance(humanTransform.position, robotTransform.position);

            if (distance < gestureDetectionRadius)
            {
                // Detect gesture based on human pose/animation
                string detectedGesture = DetectGestureFromHuman();

                if (!string.IsNullOrEmpty(detectedGesture) && gestureMap.ContainsKey(detectedGesture))
                {
                    ProcessGesture(detectedGesture);
                }
            }
        }

        // Update gesture timer
        if (handPositions.Count > 0)
        {
            gestureTimer += Time.deltaTime;
            if (gestureTimer > gestureTimeout)
            {
                handPositions.Clear();
                gestureTimer = 0f;
            }
        }
    }

    string DetectGestureFromHuman()
    {
        // In real implementation, this would use pose estimation
        // For simulation, we'll use animation state or manual input
        Animator humanAnimator = humanTransform.GetComponent<Animator>();
        if (humanAnimator != null)
        {
            // Check current animation state for gestures
            if (humanAnimator.GetCurrentAnimatorStateInfo(0).IsName("Wave"))
            {
                return "Wave";
            }
            else if (humanAnimator.GetCurrentAnimatorStateInfo(0).IsName("Point"))
            {
                return "Point";
            }
            else if (humanAnimator.GetCurrentAnimatorStateInfo(0).IsName("ComeHere"))
            {
                return "ComeHere";
            }
        }

        return null;
    }

    void ProcessGesture(string gestureName)
    {
        if (gestureMap.ContainsKey(gestureName))
        {
            GestureCommand command = gestureMap[gestureName];

            // Execute gesture command
            ExecuteGestureCommand(command);

            // Visual feedback
            ShowGestureFeedback(gestureName);
        }
    }

    void ExecuteGestureCommand(GestureCommand command)
    {
        // Convert gesture to ROS 2 command
        var rosCommand = new std_msgs.msg.String();
        rosCommand.data = command.rosCommand;

        // Publish command
        // commandPublisher.Publish(rosCommand);

        Debug.Log($"Gesture '{command.gestureName}' executed: {command.rosCommand}");
    }

    void ShowGestureFeedback(string gestureName)
    {
        // Visual feedback for gesture recognition
        Debug.Log($"Gesture recognized: {gestureName}");

        // In real implementation, update UI or show visual effects
        if (gestureVisualization != null)
        {
            // Update visualization with gesture information
        }
    }

    void OnDrawGizmos()
    {
        // Visualize gesture detection radius
        if (robotTransform != null)
        {
            Gizmos.color = Color.blue;
            Gizmos.DrawWireSphere(robotTransform.position, gestureDetectionRadius);
        }
    }
}

[System.Serializable]
public class GestureCommand
{
    public string gestureName;
    public string rosCommand;
    public float executionTime = 1.0f;
    public bool requiresConfirmation = false;
}
```

## Multimodal Interaction Interface

### Voice + Gesture + Visual Feedback

```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using TMPro;

public class MultimodalInteractionInterface : MonoBehaviour
{
    [Header("UI Components")]
    public TMP_InputField voiceCommandInput;
    public Button sendCommandButton;
    public TMP_Text statusText;
    public Image attentionIndicator;
    public Slider confidenceSlider;

    [Header("Visual Feedback")]
    public GameObject robotHead;
    public GameObject[] attentionLights;
    public ParticleSystem interactionParticles;

    [Header("Interaction Modes")]
    public InteractionMode currentMode = InteractionMode.Voice;
    public float interactionTimeout = 10.0f;

    private VoiceCommandSimulator voiceSimulator;
    private GestureRecognitionSystem gestureSystem;
    private float interactionTimer = 0f;
    private bool isInteracting = false;

    void Start()
    {
        InitializeInteractionInterface();
    }

    void InitializeInteractionInterface()
    {
        // Initialize systems
        voiceSimulator = FindObjectOfType<VoiceCommandSimulator>();
        gestureSystem = FindObjectOfType<GestureRecognitionSystem>();

        // Setup UI event handlers
        sendCommandButton.onClick.AddListener(ProcessVoiceCommand);
        voiceCommandInput.onEndEdit.AddListener(OnCommandInput);

        // Initialize UI state
        UpdateUIState();
    }

    void Update()
    {
        UpdateInteractionState();
        UpdateVisualFeedback();
    }

    void ProcessVoiceCommand()
    {
        if (!string.IsNullOrEmpty(voiceCommandInput.text))
        {
            string command = voiceCommandInput.text;

            // Simulate voice command
            if (voiceSimulator != null)
            {
                voiceSimulator.SimulateVoiceCommand(command, transform.position);
            }

            // Update UI
            statusText.text = $"Processing: {command}";
            StartInteraction();

            // Clear input
            voiceCommandInput.text = "";
        }
    }

    void OnCommandInput(string command)
    {
        // Process when user presses Enter
        if (Input.GetKeyDown(KeyCode.Return))
        {
            ProcessVoiceCommand();
        }
    }

    void UpdateInteractionState()
    {
        if (isInteracting)
        {
            interactionTimer += Time.deltaTime;
            if (interactionTimer > interactionTimeout)
            {
                EndInteraction();
            }
        }
    }

    void UpdateVisualFeedback()
    {
        // Update attention indicator based on interaction state
        if (attentionIndicator != null)
        {
            attentionIndicator.color = isInteracting ?
                Color.green : Color.gray;
        }

        // Update confidence visualization
        if (confidenceSlider != null)
        {
            // In real implementation, this would reflect actual confidence
            float simulatedConfidence = isInteracting ?
                Mathf.PingPong(Time.time * 0.5f, 1.0f) * 0.3f + 0.7f : 0f;
            confidenceSlider.value = simulatedConfidence;
        }

        // Update attention lights
        foreach (var light in attentionLights)
        {
            if (light != null)
            {
                light.color = isInteracting ?
                    Color.Lerp(Color.blue, Color.cyan, Mathf.PingPong(Time.time * 2f, 1f)) :
                    Color.gray;
            }
        }

        // Update robot head orientation
        if (robotHead != null && isInteracting)
        {
            LookAtHuman();
        }
    }

    void LookAtHuman()
    {
        // Make robot look at human
        Transform human = FindClosestHuman();
        if (human != null)
        {
            Vector3 direction = human.position - robotHead.transform.position;
            direction.y = 0; // Keep head level
            robotHead.transform.rotation = Quaternion.LookRotation(direction);
        }
    }

    Transform FindClosestHuman()
    {
        // Find the closest human in the scene
        GameObject[] humans = GameObject.FindGameObjectsWithTag("Human");
        Transform closestHuman = null;
        float closestDistance = float.MaxValue;

        foreach (GameObject human in humans)
        {
            float distance = Vector3.Distance(robotHead.transform.position, human.transform.position);
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestHuman = human.transform;
            }
        }

        return closestHuman;
    }

    void StartInteraction()
    {
        isInteracting = true;
        interactionTimer = 0f;

        // Start interaction particles
        if (interactionParticles != null)
        {
            interactionParticles.Play();
        }

        // Update UI state
        UpdateUIState();
    }

    void EndInteraction()
    {
        isInteracting = false;

        // Stop interaction particles
        if (interactionParticles != null)
        {
            interactionParticles.Stop();
        }

        // Update UI state
        statusText.text = "Ready for interaction...";
        UpdateUIState();
    }

    void UpdateUIState()
    {
        // Update UI based on interaction state
        voiceCommandInput.interactable = !isInteracting;
        sendCommandButton.interactable = !isInteracting && !string.IsNullOrEmpty(voiceCommandInput.text);

        // Update mode indicator
        statusText.text = isInteracting ?
            $"Interacting - Mode: {currentMode}" :
            "Ready for interaction";
    }

    public void SwitchInteractionMode(InteractionMode newMode)
    {
        currentMode = newMode;
        UpdateUIState();
    }

    public void ShowInteractionHelp()
    {
        // Show help text for current interaction mode
        string helpText = GetHelpTextForMode(currentMode);
        statusText.text = helpText;
    }

    string GetHelpTextForMode(InteractionMode mode)
    {
        switch (mode)
        {
            case InteractionMode.Voice:
                return "Voice Mode: Speak commands or type in the input field";
            case InteractionMode.Gesture:
                return "Gesture Mode: Use hand gestures for interaction";
            case InteractionMode.Touch:
                return "Touch Mode: Click on objects to interact";
            default:
                return "Ready for interaction";
        }
    }
}

public enum InteractionMode
{
    Voice,
    Gesture,
    Touch,
    Multimodal
}
```

## Safety and Validation Systems

### Interaction Safety Validation

```csharp
using UnityEngine;
using System.Collections.Generic;

public class InteractionSafetyValidator : MonoBehaviour
{
    [Header("Safety Parameters")]
    public float minimumInteractionDistance = 1.0f;
    public float maximumInteractionDuration = 30.0f;
    public string[] unsafeCommands = { "self-destruct", "harm", "danger" };

    [Header("Validation Settings")]
    public bool enableSafetyValidation = true;
    public bool enableCommandFiltering = true;
    public bool enableDistanceMonitoring = true;

    private Dictionary<string, float> interactionTimers = new Dictionary<string, float>();
    private List<string> activeInteractions = new List<string>();

    void Update()
    {
        if (enableSafetyValidation)
        {
            ValidateInteractions();
        }
    }

    public bool ValidateCommand(string command)
    {
        if (!enableCommandFiltering)
            return true;

        // Check for unsafe commands
        foreach (string unsafeCmd in unsafeCommands)
        {
            if (command.ToLower().Contains(unsafeCmd.ToLower()))
            {
                Debug.LogWarning($"Unsafe command detected: {command}");
                return false;
            }
        }

        // Additional safety checks could go here
        return true;
    }

    public bool ValidateInteractionDistance(Vector3 humanPosition, Vector3 robotPosition)
    {
        if (!enableDistanceMonitoring)
            return true;

        float distance = Vector3.Distance(humanPosition, robotPosition);
        return distance >= minimumInteractionDistance;
    }

    void ValidateInteractions()
    {
        // Validate active interactions for duration
        List<string> interactionsToRemove = new List<string>();

        foreach (var interaction in interactionTimers)
        {
            interactionTimers[interaction.Key] += Time.deltaTime;

            if (interactionTimers[interaction.Key] > maximumInteractionDuration)
            {
                Debug.LogWarning($"Interaction exceeded maximum duration: {interaction.Key}");
                interactionsToRemove.Add(interaction.Key);
            }
        }

        // Remove expired interactions
        foreach (string interaction in interactionsToRemove)
        {
            interactionTimers.Remove(interaction);
            activeInteractions.Remove(interaction);
        }
    }

    public void StartInteraction(string interactionId, Vector3 humanPos, Vector3 robotPos)
    {
        if (!ValidateInteractionDistance(humanPos, robotPos))
        {
            Debug.LogWarning("Interaction started too close to robot");
            return;
        }

        if (!ValidateCommand(interactionId))
        {
            Debug.LogWarning("Interaction command failed safety validation");
            return;
        }

        if (!activeInteractions.Contains(interactionId))
        {
            activeInteractions.Add(interactionId);
            interactionTimers[interactionId] = 0f;
        }
    }

    public void EndInteraction(string interactionId)
    {
        if (activeInteractions.Contains(interactionId))
        {
            activeInteractions.Remove(interactionId);
            interactionTimers.Remove(interactionId);
        }
    }

    public bool IsInteractionSafe(string interactionId, Vector3 humanPos, Vector3 robotPos)
    {
        if (!enableSafetyValidation)
            return true;

        return ValidateCommand(interactionId) &&
               ValidateInteractionDistance(humanPos, robotPos) &&
               !interactionTimers.ContainsKey(interactionId) ||
               interactionTimers[interactionId] <= maximumInteractionDuration;
    }

    void OnValidate()
    {
        // Validate inspector values
        minimumInteractionDistance = Mathf.Max(0.1f, minimumInteractionDistance);
        maximumInteractionDuration = Mathf.Max(1.0f, maximumInteractionDuration);
    }
}
```

## Integration with VLA Systems

### Unity-ROS 2 Bridge for HRI

```csharp
using UnityEngine;
using Ros2Unity;
using System.Collections;

public class HRIROS2Bridge : MonoBehaviour
{
    private ROS2UnityComponent ros2Unity;
    private Publisher interactionEventPublisher;
    private Publisher attentionStatePublisher;
    private Subscriber interactionCommandSubscriber;

    [Header("Interaction Events")]
    public string interactionEventTopic = "hri/interaction_events";
    public string attentionStateTopic = "hri/attention_state";

    [Header("Interaction Parameters")]
    public float attentionRadius = 3.0f;
    public float interactionCooldown = 1.0f;

    private float lastInteractionTime = 0f;
    private Transform currentAttentionTarget = null;

    void Start()
    {
        InitializeROS2Bridge();
    }

    void InitializeROS2Bridge()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        interactionEventPublisher = ros2Unity.CreatePublisher<std_msgs.msg.String>(interactionEventTopic);
        attentionStatePublisher = ros2Unity.CreatePublisher<std_msgs.msg.String>(attentionStateTopic);
        interactionCommandSubscriber = ros2Unity.CreateSubscriber<std_msgs.msg.String>(
            "hri/interaction_commands", InteractionCommandCallback
        );

        StartCoroutine(PublishAttentionState());
    }

    void InteractionCommandCallback(std_msgs.msg.String msg)
    {
        // Handle interaction commands from ROS 2
        string command = msg.data.ToLower();

        if (command.Contains("attention"))
        {
            SetAttentionTarget(FindObjectOfType<Camera>().transform);
        }
        else if (command.Contains("follow"))
        {
            FollowTarget(FindObjectOfType<Camera>().transform);
        }
    }

    public void PublishInteractionEvent(string eventType, string details = "")
    {
        if (Time.time - lastInteractionTime < interactionCooldown)
            return;

        var eventMsg = new std_msgs.msg.String();
        eventMsg.data = $"{{\"type\":\"{eventType}\",\"details\":\"{details}\",\"timestamp\":{Time.time}}}";

        interactionEventPublisher.Publish(eventMsg);
        lastInteractionTime = Time.time;

        Debug.Log($"Published interaction event: {eventType}");
    }

    IEnumerator PublishAttentionState()
    {
        while (true)
        {
            var attentionMsg = new std_msgs.msg.String();

            if (currentAttentionTarget != null)
            {
                attentionMsg.data = $"{{\"target\":\"{currentAttentionTarget.name}\",\"position\":[{currentAttentionTarget.position.x},{currentAttentionTarget.position.y},{currentAttentionTarget.position.z}],\"timestamp\":{Time.time}}}";
            }
            else
            {
                attentionMsg.data = $"{{\"target\":\"none\",\"position\":[0,0,0],\"timestamp\":{Time.time}}}";
            }

            attentionStatePublisher.Publish(attentionMsg);

            yield return new WaitForSeconds(0.1f); // 10Hz update rate
        }
    }

    public void SetAttentionTarget(Transform target)
    {
        currentAttentionTarget = target;
        PublishInteractionEvent("attention_set", target.name);
    }

    public void ClearAttention()
    {
        currentAttentionTarget = null;
        PublishInteractionEvent("attention_cleared");
    }

    public bool IsHumanInAttentionRange(Transform humanTransform)
    {
        if (humanTransform == null) return false;

        Transform robotTransform = this.transform; // Assuming this is attached to robot
        float distance = Vector3.Distance(humanTransform.position, robotTransform.position);
        return distance <= attentionRadius;
    }

    void OnDrawGizmos()
    {
        // Visualize attention radius
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, attentionRadius);
    }
}
```

## Best Practices for HRI Simulation

### Design Guidelines

1. **Realistic Acoustic Modeling**: Account for room acoustics, background noise, and distance effects
2. **Appropriate Interaction Distances**: Maintain safe distances for human-robot interaction
3. **Clear Feedback Mechanisms**: Provide visual, auditory, and haptic feedback
4. **Safety Validation**: Implement comprehensive safety checks for all interactions
5. **Natural Communication**: Design interactions that feel intuitive to humans
6. **Robust Error Handling**: Handle miscommunication and ambiguous commands gracefully

This human-robot interaction system enables the development and testing of sophisticated VLA systems in realistic simulation environments, ensuring safe and effective interaction patterns before deployment to physical robots.