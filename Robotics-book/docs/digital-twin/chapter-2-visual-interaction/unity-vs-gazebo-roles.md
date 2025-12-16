---
sidebar_position: 4
---

# Unity vs Gazebo Roles

## Complementary Functions in Digital Twin Architecture

Unity and Gazebo serve distinct but complementary roles in the digital twin architecture for humanoid robotics. Understanding their respective strengths and appropriate use cases is crucial for effective simulation system design and VLA system development.

## Learning Objectives

By the end of this chapter, you will:
- Understand the distinct roles of Unity and Gazebo in digital twins
- Learn when to use each platform for different simulation needs
- Design integrated workflows that leverage both platforms effectively
- Optimize resource allocation between visual and physics simulation
- Implement appropriate data exchange between Unity and Gazebo

## Platform Comparison Overview

### Gazebo: Physics-First Simulation

Gazebo excels in:
- **Accurate Physics Simulation**: Realistic rigid body dynamics, collisions, and constraints
- **Sensor Simulation**: Realistic camera, lidar, IMU, and other sensor models with noise characteristics
- **Real-time Control**: Low-latency integration with ROS 2 control systems
- **Robot Validation**: Testing control algorithms with realistic physics responses

```
[Robot Control] → [Gazebo Physics] → [Sensor Data] → [Perception]
```

### Unity: Visual-First Simulation

Unity excels in:
- **Photorealistic Rendering**: High-quality visual output for perception training
- **Flexible Environment Creation**: Easy creation of diverse, complex environments
- **Human Interaction**: Realistic human-robot interaction scenarios
- **Synthetic Data Generation**: High-quality training data for vision systems

```
[Visual Scene] → [Unity Rendering] → [Synthetic Images] → [Vision Training]
```

## Complementary Architecture

### Hybrid Simulation Approach

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Unity        │    │   Data Sync     │    │   Gazebo        │
│   (Visual)     │◄──►│   Layer         │◄──►│   (Physics)     │
│                │    │                 │    │                 │
│ • Rendering    │    │ • State Sync    │    │ • Physics       │
│ • Lighting     │    │ • Command Relay │    │ • Collisions    │
│ • Materials    │    │ • Time Sync     │    │ • Sensor Sim    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Photorealistic  │    │ Consistent      │    │ Physics-        │
│ Perception      │    │ Simulation      │    │ Accurate        │
│ Training        │    │ State           │    │ Control         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## When to Use Gazebo

### Physics-Critical Applications

```xml
<!-- Gazebo configuration for physics-critical simulation -->
<sdf version="1.7">
  <world name="physics_critical_world">
    <!-- Accurate physics engine -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>

      <ode>
        <solver>
          <type>quick</type>  <!-- High accuracy solver -->
          <iters>100</iters>   <!-- More iterations for stability -->
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0.000001</cfm>  <!-- Very tight constraints -->
          <erp>0.2</erp>
        </constraints>
      </ode>
    </physics>

    <!-- Robot with accurate physical properties -->
    <model name="humanoid_robot">
      <pose>0 0 1.0 0 0 0</pose>

      <!-- Links with precise mass and inertia -->
      <link name="base_link">
        <inertial>
          <mass>15.0</mass>
          <inertia>
            <ixx>0.5</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>0.5</iyy>
            <iyz>0.0</iyz>
            <izz>0.5</izz>
          </inertia>
        </inertial>

        <!-- Accurate collision geometry -->
        <collision name="collision">
          <geometry>
            <mesh>
              <uri>model://humanoid/meshes/base_collision.stl</uri>
            </mesh>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.8</mu>
                <mu2>0.8</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
      </link>
    </model>
  </world>
</sdf>
```

### Control System Validation

Gazebo is ideal for:
- **Locomotion Control**: Testing walking, running, and balance algorithms
- **Manipulation Control**: Validating grasping and manipulation strategies
- **Sensor Fusion**: Testing integration of multiple sensor systems
- **Real-time Performance**: Low-latency control loop testing

### Sensor Simulation

```xml
<!-- Accurate sensor simulation in Gazebo -->
<gazebo reference="camera_link">
  <sensor name="rgb_camera" type="camera">
    <update_rate>30</update_rate>
    <camera name="head_camera">
      <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>10.0</far>
      </clip>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>  <!-- Realistic noise level -->
      </noise>
    </camera>
    <always_on>true</always_on>
    <visualize>true</visualize>
  </sensor>
</gazebo>

<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -π -->
          <max_angle>3.14159</max_angle>   <!-- π -->
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="ray_plugin" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>lidar</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</gazebo>
```

## When to Use Unity

### Perception System Development

Unity is ideal for:
- **Synthetic Data Generation**: High-quality images for vision training
- **Photorealistic Rendering**: Training data that bridges simulation-to-reality gap
- **Visual Validation**: Testing perception algorithms with realistic visuals
- **Human Interaction**: Realistic human-robot interaction scenarios

### C# Implementation Example

```csharp
using UnityEngine;
using System.Collections;

public class UnityPerceptionSimulation : MonoBehaviour
{
    [Header("Camera Configuration")]
    public Camera perceptionCamera;
    public int imageWidth = 1280;
    public int imageHeight = 720;
    public int captureRate = 30; // FPS

    [Header("Rendering Quality")]
    public bool useHDR = true;
    public bool usePostProcessing = false; // Disable for synthetic data consistency
    public int antiAliasing = 2;

    private RenderTexture renderTexture;
    private int frameCounter = 0;
    private int sequenceNumber = 0;

    void Start()
    {
        SetupPerceptionCamera();
        InitializeRenderTexture();
    }

    void SetupPerceptionCamera()
    {
        perceptionCamera.allowHDR = useHDR;
        perceptionCamera.allowMSAA = antiAliasing > 1;
        perceptionCamera.clearFlags = CameraClearFlags.SolidColor;
        perceptionCamera.backgroundColor = Color.black;
    }

    void InitializeRenderTexture()
    {
        renderTexture = new RenderTexture(imageWidth, imageHeight, 24, RenderTextureFormat.ARGB32);
        renderTexture.Create();
        perceptionCamera.targetTexture = renderTexture;
    }

    void Update()
    {
        if (frameCounter % (60 / captureRate) == 0) // Unity runs at 60 FPS
        {
            CapturePerceptionData();
        }
        frameCounter = (frameCounter + 1) % 60;
    }

    void CapturePerceptionData()
    {
        // Capture high-quality image for perception training
        RenderTexture.active = renderTexture;
        Texture2D imageTexture = new Texture2D(renderTexture.width, renderTexture.height,
                                               TextureFormat.RGB24, false);
        imageTexture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        imageTexture.Apply();

        // Save with sequence number for training data
        string fileName = $"synthetic_image_{sequenceNumber:D6}.png";
        string filePath = System.IO.Path.Combine(Application.persistentDataPath, "PerceptionData", fileName);

        System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(filePath));
        System.IO.File.WriteAllBytes(filePath, imageTexture.EncodeToPNG());

        // Publish to ROS 2 if needed
        // PublishToROS2(imageTexture);

        sequenceNumber++;
        DestroyImmediate(imageTexture);

        Debug.Log($"Captured perception image: {fileName}");
    }

    void OnValidate()
    {
        // Ensure valid capture rate
        captureRate = Mathf.Clamp(captureRate, 1, 60);
        imageWidth = Mathf.Clamp(imageWidth, 64, 3840);  // Max 4K
        imageHeight = Mathf.Clamp(imageHeight, 64, 2160);
    }
}
```

### Environment Creation and Management

```csharp
using UnityEngine;
using System.Collections.Generic;

public class UnityEnvironmentManager : MonoBehaviour
{
    [Header("Environment Types")]
    public GameObject[] kitchenPrefabs;
    public GameObject[] livingRoomPrefabs;
    public GameObject[] bedroomPrefabs;

    [Header("Lighting Configuration")]
    public Gradient dayNightCycle;
    public float timeScale = 1.0f;

    [Header("Procedural Generation")]
    public bool enableProceduralGeneration = true;
    public int minObjectsPerRoom = 5;
    public int maxObjectsPerRoom = 15;

    private float simulationTime = 0f;
    private List<GameObject> spawnedObjects = new List<GameObject>();

    void Start()
    {
        if (enableProceduralGeneration)
        {
            GenerateEnvironment();
        }
        else
        {
            SetupStaticEnvironment();
        }
    }

    void Update()
    {
        UpdateEnvironmentConditions();
    }

    void GenerateEnvironment()
    {
        // Create multiple rooms with different object types
        CreateRoom("Kitchen", kitchenPrefabs, new Vector3(0, 0, 0));
        CreateRoom("LivingRoom", livingRoomPrefabs, new Vector3(8, 0, 0));
        CreateRoom("Bedroom", bedroomPrefabs, new Vector3(0, 0, 8));
    }

    void CreateRoom(string roomName, GameObject[] prefabs, Vector3 position)
    {
        int objectCount = Random.Range(minObjectsPerRoom, maxObjectsPerRoom + 1);

        for (int i = 0; i < objectCount; i++)
        {
            // Randomly select object from available prefabs
            GameObject prefab = prefabs[Random.Range(0, prefabs.Length)];

            // Position within room bounds
            Vector3 spawnPosition = position + new Vector3(
                Random.Range(-3f, 3f),
                0,
                Random.Range(-2f, 2f)
            );

            GameObject spawnedObject = Instantiate(prefab, spawnPosition, Quaternion.identity);
            spawnedObject.name = $"{roomName}_{prefab.name}_{i}";
            spawnedObjects.Add(spawnedObject);
        }
    }

    void SetupStaticEnvironment()
    {
        // Load pre-built environment from scene
        // This would typically be done through Unity's scene system
    }

    void UpdateEnvironmentConditions()
    {
        simulationTime += Time.deltaTime * timeScale;

        // Update lighting based on time of day
        UpdateLightingConditions();

        // Update environmental effects (if any)
        UpdateEnvironmentalEffects();
    }

    void UpdateLightingConditions()
    {
        // Update environment lighting based on simulated time
        float timeOfDay = (simulationTime % 86400) / 86400f; // Normalize to 0-1 (24 hours)
        Color lightColor = dayNightCycle.Evaluate(timeOfDay);

        // Apply to directional light
        Light[] lights = FindObjectsOfType<Light>();
        foreach (Light light in lights)
        {
            if (light.type == LightType.Directional)
            {
                light.color = lightColor;
                light.intensity = 0.5f + (timeOfDay * 0.5f); // Vary intensity through day
            }
        }
    }

    void UpdateEnvironmentalEffects()
    {
        // Update any environmental effects like weather, etc.
        // This could include particle systems, post-processing effects, etc.
    }

    public void ChangeEnvironmentTime(float newTimeOfDay)
    {
        // Change to specific time of day (0-1 scale)
        simulationTime = newTimeOfDay * 86400f;
    }

    void OnDestroy()
    {
        // Clean up spawned objects
        foreach (GameObject obj in spawnedObjects)
        {
            if (obj != null)
            {
                DestroyImmediate(obj);
            }
        }
        spawnedObjects.Clear();
    }
}
```

## Integration Strategies

### Data Synchronization Layer

```csharp
using UnityEngine;
using Ros2Unity;
using System.Collections.Generic;

public class SimulationSynchronization : MonoBehaviour
{
    [Header("Synchronization Settings")]
    public float syncRate = 60.0f; // Hz
    public float maxSyncError = 0.01f; // Maximum allowed sync error

    [Header("State Topics")]
    public string gazeboStateTopic = "gazebo/model_states";
    public string unityStateTopic = "unity/robot_states";
    public string commandTopic = "joint_commands";

    private ROS2UnityComponent ros2Unity;
    private Subscriber gazeboStateSubscriber;
    private Publisher unityStatePublisher;
    private Subscriber commandSubscriber;

    private Dictionary<string, RobotState> robotStates = new Dictionary<string, RobotState>();
    private float lastSyncTime = 0f;

    void Start()
    {
        InitializeSynchronization();
    }

    void InitializeSynchronization()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        // Subscribe to Gazebo state updates
        gazeboStateSubscriber = ros2Unity.CreateSubscriber<gazebo_msgs.msg.ModelStates>(
            gazeboStateTopic, GazeboStateCallback
        );

        // Publish Unity state updates
        unityStatePublisher = ros2Unity.CreatePublisher<gazebo_msgs.msg.ModelStates>(
            unityStateTopic
        );

        // Subscribe to joint commands
        commandSubscriber = ros2Unity.CreateSubscriber<sensor_msgs.msg.JointState>(
            commandTopic, JointCommandCallback
        );
    }

    void Update()
    {
        if (Time.time - lastSyncTime >= 1.0f / syncRate)
        {
            SynchronizeStates();
            lastSyncTime = Time.time;
        }
    }

    void GazeboStateCallback(gazebo_msgs.msg.ModelStates msg)
    {
        // Update Unity representation based on Gazebo state
        for (int i = 0; i < msg.name.Count; i++)
        {
            string modelName = msg.name[i];
            geometry_msgs.msg.Pose pose = msg.pose[i];

            if (robotStates.ContainsKey(modelName))
            {
                robotStates[modelName].position = ConvertROS2UnityPosition(pose.position);
                robotStates[modelName].rotation = ConvertROS2UnityRotation(pose.orientation);
            }
            else
            {
                robotStates[modelName] = new RobotState
                {
                    position = ConvertROS2UnityPosition(pose.position),
                    rotation = ConvertROS2UnityRotation(pose.orientation)
                };
            }

            // Update Unity object transform
            UpdateUnityObject(modelName, robotStates[modelName]);
        }
    }

    void JointCommandCallback(sensor_msgs.msg.JointState msg)
    {
        // Forward joint commands to Unity robot representation
        // This would update the Unity robot's joint positions/velocities
        ApplyJointCommandsToUnity(msg);
    }

    void SynchronizeStates()
    {
        // Publish Unity state to maintain synchronization
        var unityStateMsg = new gazebo_msgs.msg.ModelStates();

        foreach (var statePair in robotStates)
        {
            unityStateMsg.name.Add(statePair.Key);

            var pose = new geometry_msgs.msg.Pose();
            pose.position = ConvertUnity2ROSPos(statePair.Value.position);
            pose.orientation = ConvertUnity2ROSRot(statePair.Value.rotation);
            unityStateMsg.pose.Add(pose);

            // Add twist (velocity) information
            var twist = new geometry_msgs.msg.Twist();
            unityStateMsg.twist.Add(twist);
        }

        unityStatePublisher.Publish(unityStateMsg);
    }

    Vector3 ConvertROS2UnityPosition(geometry_msgs.msg.Point rosPoint)
    {
        // Convert ROS coordinate system to Unity (ROS: right-handed, Unity: left-handed)
        return new Vector3(rosPoint.x, rosPoint.z, rosPoint.y);
    }

    Quaternion ConvertROS2UnityRotation(geometry_msgs.msg.Quaternion rosQuat)
    {
        // Convert ROS quaternion to Unity quaternion
        return new Quaternion(rosQuat.x, rosQuat.z, rosQuat.y, rosQuat.w);
    }

    geometry_msgs.msg.Point ConvertUnity2ROSPos(Vector3 unityPos)
    {
        // Convert Unity position to ROS
        var rosPoint = new geometry_msgs.msg.Point();
        rosPoint.x = unityPos.x;
        rosPoint.y = unityPos.z;
        rosPoint.z = unityPos.y;
        return rosPoint;
    }

    geometry_msgs.msg.Quaternion ConvertUnity2ROSRot(Quaternion unityRot)
    {
        // Convert Unity rotation to ROS
        var rosQuat = new geometry_msgs.msg.Quaternion();
        rosQuat.x = unityRot.x;
        rosQuat.y = unityRot.z;
        rosQuat.z = unityRot.y;
        rosQuat.w = unityRot.w;
        return rosQuat;
    }

    void UpdateUnityObject(string modelName, RobotState state)
    {
        // Find and update the corresponding Unity object
        GameObject unityObject = GameObject.Find(modelName);
        if (unityObject != null)
        {
            unityObject.transform.position = state.position;
            unityObject.transform.rotation = state.rotation;
        }
    }

    void ApplyJointCommandsToUnity(sensor_msgs.msg.JointState jointState)
    {
        // Apply joint commands to Unity robot model
        // This would involve updating the Unity robot's articulation body or animation
        for (int i = 0; i < jointState.name.Count; i++)
        {
            string jointName = jointState.name[i];
            double position = jointState.position[i];

            // Update corresponding joint in Unity robot
            UpdateUnityJoint(jointName, (float)position);
        }
    }

    void UpdateUnityJoint(string jointName, float position)
    {
        // Find and update the joint in the Unity robot model
        Transform jointTransform = transform.Find("Robot/Joints/" + jointName);
        if (jointTransform != null)
        {
            // Apply position update (implementation depends on joint type)
            // For example, if it's a hinge joint:
            jointTransform.localRotation = Quaternion.Euler(0, 0, position * Mathf.Rad2Deg);
        }
    }
}

[System.Serializable]
public class RobotState
{
    public Vector3 position;
    public Quaternion rotation;
    public Vector3 velocity;
    public Vector3 angularVelocity;
}
```

## Resource Allocation Strategies

### Performance Optimization

```csharp
using UnityEngine;

public class ResourceAllocationManager : MonoBehaviour
{
    [Header("Unity Resource Allocation")]
    public int maxRenderTextures = 4;
    public int maxLightSources = 8;
    public int maxAudioSources = 16;

    [Header("Performance Targets")]
    public float targetFrameRate = 60.0f;
    public float maxRenderTimeMs = 16.0f; // 1 frame at 60 FPS
    public float maxPhysicsTimeMs = 8.0f;  // Half frame time

    [Header("Quality Scaling")]
    public bool enableDynamicQuality = true;
    public float qualityAdjustmentThreshold = 0.8f; // 80% of target

    private float[] frameTimes = new float[60]; // Last 60 frames
    private int frameIndex = 0;
    private float averageFrameTime = 0f;

    void Start()
    {
        InitializeResourceLimits();
    }

    void Update()
    {
        UpdatePerformanceMetrics();
        AdjustQualityBasedOnPerformance();
    }

    void InitializeResourceLimits()
    {
        // Set Unity quality settings based on target performance
        Application.targetFrameRate = Mathf.RoundToInt(targetFrameRate);

        // Configure rendering limits
        QualitySettings.maxQueuedFrames = 2;
        QualitySettings.vSyncCount = 0; // Manual vsync control

        // Initialize performance tracking
        for (int i = 0; i < frameTimes.Length; i++)
        {
            frameTimes[i] = 1.0f / targetFrameRate;
        }
    }

    void UpdatePerformanceMetrics()
    {
        float currentFrameTime = Time.deltaTime;
        frameTimes[frameIndex] = currentFrameTime;
        frameIndex = (frameIndex + 1) % frameTimes.Length;

        // Calculate average frame time
        float sum = 0f;
        for (int i = 0; i < frameTimes.Length; i++)
        {
            sum += frameTimes[i];
        }
        averageFrameTime = sum / frameTimes.Length;

        // Calculate performance ratio
        float performanceRatio = (1.0f / targetFrameRate) / averageFrameTime;

        Debug.Log($"Performance: {1.0f/averageFrameTime:F1} FPS ({performanceRatio:P1} of target)");
    }

    void AdjustQualityBasedOnPerformance()
    {
        if (!enableDynamicQuality) return;

        float performanceRatio = (1.0f / targetFrameRate) / averageFrameTime;

        if (performanceRatio < qualityAdjustmentThreshold)
        {
            // Performance is below threshold, reduce quality
            ReduceQualitySettings();
        }
        else if (performanceRatio > qualityAdjustmentThreshold * 1.2f)
        {
            // Performance is significantly above threshold, can increase quality
            IncreaseQualitySettings();
        }
    }

    void ReduceQualitySettings()
    {
        // Reduce rendering quality to maintain performance
        var currentQuality = QualitySettings.GetQualityLevel();

        if (currentQuality > 0)
        {
            QualitySettings.SetQualityLevel(currentQuality - 1, true);
            Debug.Log($"Reduced quality level to {currentQuality - 1}");
        }

        // Reduce shadow distance
        QualitySettings.shadowDistance = Mathf.Max(10f, QualitySettings.shadowDistance * 0.9f);

        // Reduce texture quality
        QualitySettings.masterTextureLimit = Mathf.Min(3, QualitySettings.masterTextureLimit + 1);
    }

    void IncreaseQualitySettings()
    {
        // Increase quality if performance allows
        var currentQuality = QualitySettings.GetQualityLevel();
        var maxQuality = QualitySettings.names.Length - 1;

        if (currentQuality < maxQuality)
        {
            QualitySettings.SetQualityLevel(currentQuality + 1, true);
            Debug.Log($"Increased quality level to {currentQuality + 1}");
        }

        // Gradually increase shadow distance
        QualitySettings.shadowDistance = Mathf.Min(100f, QualitySettings.shadowDistance * 1.1f);

        // Improve texture quality
        QualitySettings.masterTextureLimit = Mathf.Max(0, QualitySettings.masterTextureLimit - 1);
    }

    public void OptimizeForGazeboIntegration()
    {
        // Optimize Unity settings when Gazebo is the primary physics engine
        QualitySettings.shadowResolution = UnityEngine.Rendering.ShadowResolution.Medium;
        QualitySettings.shadowDistance = 30f; // Balance quality with performance
        QualitySettings.shadowCascades = 2;   // Reduce from 4 to 2 for performance

        // Disable expensive effects that don't affect Gazebo data
        RenderSettings.fog = false;
        QualitySettings.billboardsFaceCameraPosition = false;
    }

    public void OptimizeForPerceptionTraining()
    {
        // Optimize Unity settings when focused on perception training
        QualitySettings.shadowResolution = UnityEngine.Rendering.ShadowResolution.High;
        QualitySettings.shadowDistance = 50f; // Larger area for training
        QualitySettings.shadowCascades = 4;   // Higher quality shadows

        // Enable effects that improve visual quality for training
        RenderSettings.fog = true;
        QualitySettings.billboardsFaceCameraPosition = true;
    }
}
```

## Best Practices for Platform Selection

### Decision Framework

1. **Use Gazebo when:**
   - Physics accuracy is critical (locomotion, manipulation)
   - Real-time control system validation is needed
   - Sensor simulation accuracy is paramount
   - Low-latency interaction is required

2. **Use Unity when:**
   - Photorealistic rendering is needed for perception
   - Flexible environment creation is important
   - Human interaction scenarios are being tested
   - Synthetic data generation is the primary goal

3. **Use both when:**
   - Comprehensive VLA system validation is required
   - Both physics and visual fidelity are important
   - Training and validation across different domains is needed

### Integration Patterns

- **Loose Coupling**: Minimal data exchange between platforms
- **Tight Integration**: Real-time synchronization of states
- **Pipeline Approach**: Sequential use of each platform for different tasks
- **Hybrid Simulation**: Parallel operation with selective data exchange

This complementary approach leverages the strengths of both platforms to create comprehensive digital twins for humanoid robot development and VLA system validation.