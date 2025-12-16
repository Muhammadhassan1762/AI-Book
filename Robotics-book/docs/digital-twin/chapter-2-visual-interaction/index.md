---
sidebar_position: 1
---

# Visual & Interaction Simulation with Unity

## High-Fidelity Rendering and Human-Robot Interaction

Unity provides the visual foundation for digital twins, enabling photorealistic rendering and sophisticated interaction simulation. For humanoid robots, Unity integration allows for high-fidelity visual simulation that complements physics simulation and enables realistic perception system testing.

## Learning Objectives

By the end of this chapter, you will:
- Understand Unity's role in robotics simulation and digital twins
- Learn to create high-fidelity visual environments for humanoid robots
- Implement realistic rendering and lighting for perception systems
- Integrate Unity with ROS 2 for human-robot interaction simulation
- Apply visual simulation to VLA system development and testing

## Unity in the Robotics Digital Twin

Unity serves as the visual layer of the digital twin, providing:

- **Photorealistic rendering**: High-quality visual output for perception systems
- **Flexible environment creation**: Easy creation of diverse test environments
- **Realistic lighting and materials**: Accurate visual simulation
- **Human-in-the-loop interaction**: Realistic human-robot interaction scenarios
- **Synthetic data generation**: Training data for vision systems

### Architecture Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Unity        │    │   Perception    │    │   Control       │
│   (Visual)     │───▶│   (Cameras,     │───▶│   Systems       │
│                │    │   Sensors)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ High-Fidelity   │    │ Realistic       │    │ Same Control    │
│ Rendering       │    │ Sensor Data     │    │ Code (ROS 2)    │
│ (Photorealistic)│    │ (Synthetic)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Unity-ROS 2 Integration

### ROS 2 For Unity Package

Unity integrates with ROS 2 through the ROS 2 For Unity package:

```csharp
using Ros2Unity;
using UnityEngine;

public class UnityRobotController : MonoBehaviour
{
    private ROS2UnityComponent ros2Unity;
    private Publisher positionCommandPublisher;

    void Start()
    {
        // Initialize ROS 2 connection
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        // Create publisher for robot commands
        positionCommandPublisher = ros2Unity.CreatePublisher<JointStateMsg>(
            "unity_joint_commands"
        );
    }

    void Update()
    {
        // Send joint positions to ROS 2
        SendJointPositions();
    }

    void SendJointPositions()
    {
        var jointState = new JointStateMsg();
        jointState.name = new string[] { "joint1", "joint2", "joint3" };
        jointState.position = new double[] {
            transform.localEulerAngles.x,
            transform.localEulerAngles.y,
            transform.localEulerAngles.z
        };

        positionCommandPublisher.Publish(jointState);
    }
}
```

### Camera Integration for Perception

Unity cameras can publish images to ROS 2 for perception system testing:

```csharp
using UnityEngine;
using Ros2Unity;

public class UnityCameraPublisher : MonoBehaviour
{
    public Camera unityCamera;
    public string topicName = "unity_camera/image_raw";
    public int publishRate = 30; // Hz

    private ROS2UnityComponent ros2Unity;
    private Publisher imagePublisher;
    private RenderTexture renderTexture;
    private int frameCount = 0;

    void Start()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        imagePublisher = ros2Unity.CreatePublisher<ImageMsg>(topicName);

        // Create render texture for camera output
        renderTexture = new RenderTexture(640, 480, 24);
        unityCamera.targetTexture = renderTexture;
    }

    void Update()
    {
        if (frameCount % (60 / publishRate) == 0) // 60 FPS Unity
        {
            PublishCameraImage();
        }
        frameCount++;
    }

    void PublishCameraImage()
    {
        RenderTexture.active = renderTexture;
        Texture2D imageTexture = new Texture2D(renderTexture.width, renderTexture.height,
                                               TextureFormat.RGB24, false);
        imageTexture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        imageTexture.Apply();

        // Convert to ROS 2 Image message
        ImageMsg imageMsg = new ImageMsg();
        imageMsg.header.stamp = GetROSTimestamp();
        imageMsg.header.frame_id = "unity_camera_optical_frame";
        imageMsg.height = (uint)renderTexture.height;
        imageMsg.width = (uint)renderTexture.width;
        imageMsg.encoding = "rgb8";
        imageMsg.is_bigendian = 0;
        imageMsg.step = (uint)(renderTexture.width * 3); // 3 bytes per pixel
        imageMsg.data = Texture2DToByteArray(imageTexture);

        imagePublisher.Publish(imageMsg);

        Destroy(imageTexture);
    }

    byte[] Texture2DToByteArray(Texture2D texture)
    {
        // Convert Texture2D to byte array for ROS message
        Color32[] colors = texture.GetPixels32();
        byte[] bytes = new byte[colors.Length * 3]; // RGB

        for (int i = 0; i < colors.Length; i++)
        {
            bytes[i * 3] = colors[i].r;
            bytes[i * 3 + 1] = colors[i].g;
            bytes[i * 3 + 2] = colors[i].b;
        }

        return bytes;
    }

    builtin_interfaces.msg.Time GetROSTimestamp()
    {
        // Get current ROS timestamp
        builtin_interfaces.msg.Time time = new builtin_interfaces.msg.Time();
        System.TimeSpan timeSpan = System.DateTime.UtcNow - new System.DateTime(1970, 1, 1);
        time.sec = (int)timeSpan.TotalSeconds;
        time.nanosec = (uint)(timeSpan.Milliseconds * 1000000);
        return time;
    }
}
```

## High-Fidelity Rendering

### Material and Shader Configuration

For realistic humanoid robot rendering:

```csharp
using UnityEngine;

public class HumanoidMaterialSetup : MonoBehaviour
{
    public Material skinMaterial;
    public Material metalMaterial;
    public Material fabricMaterial;

    void Start()
    {
        SetupSkinMaterial();
        SetupMetalMaterial();
        SetupFabricMaterial();
    }

    void SetupSkinMaterial()
    {
        // Configure realistic skin material
        skinMaterial.SetColor("_BaseColor", new Color(0.8f, 0.6f, 0.4f, 1.0f)); // Skin tone
        skinMaterial.SetFloat("_Metallic", 0.0f); // Non-metallic
        skinMaterial.SetFloat("_Smoothness", 0.3f); // Subtle gloss
        skinMaterial.EnableKeyword("_NORMALMAP");
    }

    void SetupMetalMaterial()
    {
        // Configure realistic metal material
        metalMaterial.SetColor("_BaseColor", new Color(0.5f, 0.5f, 0.5f, 1.0f)); // Gray metal
        metalMaterial.SetFloat("_Metallic", 0.9f); // Highly metallic
        metalMaterial.SetFloat("_Smoothness", 0.7f); // Shiny
    }

    void SetupFabricMaterial()
    {
        // Configure fabric material for clothing
        fabricMaterial.SetColor("_BaseColor", new Color(0.2f, 0.4f, 0.8f, 1.0f)); // Blue fabric
        metalMaterial.SetFloat("_Metallic", 0.0f); // Non-metallic
        metalMaterial.SetFloat("_Smoothness", 0.1f); // Matte
        fabricMaterial.EnableKeyword("_ALPHATEST_ON"); // Enable transparency if needed
    }
}
```

### Lighting Setup for Realistic Perception

```csharp
using UnityEngine;

public class RealisticLightingSetup : MonoBehaviour
{
    public Light mainLight;
    public Light fillLight;
    public Light rimLight;

    void Start()
    {
        ConfigureMainLight();
        ConfigureFillLight();
        ConfigureRimLight();
    }

    void ConfigureMainLight()
    {
        // Main directional light (sun/simulation light)
        mainLight.type = LightType.Directional;
        mainLight.color = Color.white;
        mainLight.intensity = 1.0f;
        mainLight.shadows = LightShadows.Soft;
        mainLight.shadowStrength = 0.8f;
        mainLight.transform.rotation = Quaternion.Euler(50, -30, 0);
    }

    void ConfigureFillLight()
    {
        // Fill light to reduce harsh shadows
        fillLight.type = LightType.Directional;
        fillLight.color = new Color(0.4f, 0.4f, 0.5f, 1.0f); // Cool fill
        fillLight.intensity = 0.3f;
        fillLight.shadows = LightShadows.None;
        fillLight.transform.rotation = Quaternion.Euler(-40, 150, 0);
    }

    void ConfigureRimLight()
    {
        // Rim light for better object definition
        rimLight.type = LightType.Directional;
        rimLight.color = Color.white;
        rimLight.intensity = 0.2f;
        rimLight.shadows = LightShadows.None;
        rimLight.transform.rotation = Quaternion.Euler(20, 200, 0);
    }

    void Update()
    {
        // Add dynamic lighting variations for realism
        float timeVariation = Mathf.Sin(Time.time * 0.1f) * 0.1f;
        mainLight.intensity = 1.0f + timeVariation;
    }
}
```

## Environment Creation

### Procedural Environment Generation

```csharp
using UnityEngine;
using System.Collections.Generic;

public class ProceduralEnvironmentGenerator : MonoBehaviour
{
    public GameObject[] furniturePrefabs;
    public Transform environmentParent;

    [Header("Environment Parameters")]
    public int roomCount = 5;
    public float roomSize = 5f;
    public Vector2Int objectCountRange = new Vector2Int(3, 8);

    void Start()
    {
        GenerateEnvironment();
    }

    void GenerateEnvironment()
    {
        for (int i = 0; i < roomCount; i++)
        {
            GenerateRoom(i);
        }
    }

    void GenerateRoom(int roomIndex)
    {
        // Create room boundaries
        Vector3 roomPosition = new Vector3(
            (roomIndex % 3) * (roomSize + 2),
            0,
            (roomIndex / 3) * (roomSize + 2)
        );

        // Add objects to room
        int objectCount = Random.Range(objectCountRange.x, objectCountRange.y + 1);

        for (int j = 0; j < objectCount; j++)
        {
            SpawnRandomObject(roomPosition);
        }
    }

    void SpawnRandomObject(Vector3 roomPosition)
    {
        GameObject prefab = furniturePrefabs[Random.Range(0, furniturePrefabs.Length)];
        Vector3 spawnPosition = roomPosition + new Vector3(
            Random.Range(-roomSize/2, roomSize/2),
            0,
            Random.Range(-roomSize/2, roomSize/2)
        );

        GameObject spawnedObject = Instantiate(prefab, spawnPosition, Quaternion.identity, environmentParent);

        // Add random rotation
        spawnedObject.transform.rotation = Quaternion.Euler(
            0, Random.Range(0, 360), 0
        );
    }
}
```

## Human-Robot Interaction Simulation

### Voice Command Simulation

```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class VoiceCommandSimulator : MonoBehaviour
{
    public InputField commandInput;
    public Button sendCommandButton;
    public Text statusText;

    private ROS2UnityComponent ros2Unity;
    private Publisher commandPublisher;

    void Start()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        commandPublisher = ros2Unity.CreatePublisher<std_msgs.msg.String>("vla_commands");

        sendCommandButton.onClick.AddListener(SendCommand);
    }

    void SendCommand()
    {
        if (!string.IsNullOrEmpty(commandInput.text))
        {
            // Publish command to ROS 2
            var commandMsg = new std_msgs.msg.String();
            commandMsg.data = commandInput.text;

            commandPublisher.Publish(commandMsg);

            statusText.text = $"Command sent: {commandInput.text}";

            // Clear input
            commandInput.text = "";

            StartCoroutine(ClearStatusText());
        }
    }

    IEnumerator ClearStatusText()
    {
        yield return new WaitForSeconds(3f);
        statusText.text = "Ready for command...";
    }
}
```

## Synthetic Data Generation

### Training Data Pipeline

```csharp
using UnityEngine;
using System.Collections;
using System.IO;

public class SyntheticDataGenerator : MonoBehaviour
{
    public Camera dataCamera;
    public string dataOutputPath = "SyntheticData/";
    public int imageWidth = 640;
    public int imageHeight = 480;
    public int captureRate = 10; // Hz

    private RenderTexture renderTexture;
    private int frameCounter = 0;
    private int sequenceNumber = 0;

    void Start()
    {
        // Create output directory
        Directory.CreateDirectory(Path.Combine(Application.persistentDataPath, dataOutputPath));

        // Setup render texture
        renderTexture = new RenderTexture(imageWidth, imageHeight, 24);
        dataCamera.targetTexture = renderTexture;
    }

    void Update()
    {
        if (frameCounter % (60 / captureRate) == 0) // 60 FPS Unity
        {
            CaptureTrainingData();
        }
        frameCounter++;
    }

    void CaptureTrainingData()
    {
        // Capture RGB image
        RenderTexture.active = renderTexture;
        Texture2D rgbTexture = new Texture2D(renderTexture.width, renderTexture.height,
                                            TextureFormat.RGB24, false);
        rgbTexture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        rgbTexture.Apply();

        // Save RGB image
        string rgbPath = Path.Combine(Application.persistentDataPath,
                                    dataOutputPath,
                                    $"rgb_{sequenceNumber:D6}.png");
        File.WriteAllBytes(rgbPath, rgbTexture.EncodeToPNG());
        Destroy(rgbTexture);

        // Capture depth image (if available)
        CaptureDepthImage();

        // Generate annotation data
        GenerateAnnotationData();

        sequenceNumber++;
    }

    void CaptureDepthImage()
    {
        // Render depth to texture and save
        // Implementation depends on your depth rendering setup
    }

    void GenerateAnnotationData()
    {
        // Generate bounding boxes, segmentation masks, etc.
        // Save as JSON or other annotation format
    }
}
```

## Performance Optimization

### Unity Performance Settings for Real-time Simulation

```csharp
using UnityEngine;

public class UnityPerformanceOptimizer : MonoBehaviour
{
    [Header("Performance Settings")]
    public int targetFrameRate = 60;
    public bool useVSync = false;
    public int lodBias = 1;

    [Header("Quality Settings")]
    public int shadowResolution = 2; // High
    public int textureQuality = 1; // High
    public int anisotropicFiltering = 2; // 4x

    void Start()
    {
        ApplyPerformanceSettings();
    }

    void ApplyPerformanceSettings()
    {
        // Set target frame rate
        Application.targetFrameRate = targetFrameRate;
        QualitySettings.vSyncCount = useVSync ? 1 : 0;

        // Set level of detail bias
        QualitySettings.lodBias = lodBias;

        // Set shadow resolution
        QualitySettings.shadowResolution = (ShadowResolution)shadowResolution;

        // Set texture quality
        QualitySettings.masterTextureLimit = textureQuality;

        // Set anisotropic filtering
        QualitySettings.anisotropicFiltering = (AnisotropicFiltering)anisotropicFiltering;

        // Disable expensive effects if needed
        RenderSettings.fog = false; // Disable fog for performance
    }

    void Update()
    {
        // Monitor performance and adjust if needed
        float frameTime = 1.0f / Time.smoothDeltaTime;
        if (frameTime < targetFrameRate * 0.8f) // 80% of target
        {
            // Reduce quality if frame rate is too low
            ReduceQuality();
        }
    }

    void ReduceQuality()
    {
        // Temporarily reduce quality to maintain performance
        QualitySettings.shadowDistance = Mathf.Max(20f, QualitySettings.shadowDistance * 0.9f);
    }
}
```

## Integration with VLA Systems

Unity visual simulation enables:
- **Synthetic data generation**: Training data for vision systems
- **Perception validation**: Testing vision algorithms in photorealistic environments
- **Human interaction**: Realistic human-robot interaction scenarios
- **Voice command testing**: Visual feedback for voice-activated actions
- **Safety validation**: Testing responses to visual obstacles and hazards

## Best Practices

1. **Balance quality with performance**: Maintain real-time simulation rates
2. **Use appropriate textures**: Realistic but optimized for performance
3. **Validate visual fidelity**: Ensure synthetic data matches real sensor data
4. **Optimize for target hardware**: Consider computational constraints
5. **Document rendering parameters**: Record settings for reproducibility
6. **Test perception systems**: Validate that vision algorithms work with synthetic data

This Unity integration provides the high-fidelity visual simulation necessary for developing and testing humanoid robots with vision-language-action capabilities in realistic environments.