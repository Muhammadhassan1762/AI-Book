---
sidebar_position: 1
---

# Sensor Simulation

## Realistic Sensor Data for Humanoid Robot Perception

Sensor simulation is a critical component of digital twins for humanoid robots, providing realistic sensor data that enables the development and validation of perception systems. This chapter covers the simulation of various sensors including cameras, lidars, IMUs, and other sensors essential for vision-language-action systems.

## Learning Objectives

By the end of this chapter, you will:
- Understand the principles of realistic sensor simulation
- Implement camera, lidar, and IMU simulation with realistic noise models
- Configure sensor parameters to match real hardware specifications
- Validate sensor simulation accuracy against real sensor data
- Apply sensor simulation to VLA system development and testing

## Sensor Simulation Fundamentals

### The Sensor Simulation Pipeline

```
[Physical World] → [Sensor Model] → [Noise Application] → [Data Conversion] → [ROS 2 Message]
     ↑                   ↑                  ↑                   ↑                ↑
Real Environment    Physical Model    Realistic Noise    Format Conversion   ROS Interface
```

For humanoid robots, sensor simulation must account for:
- **Physical properties**: Field of view, resolution, range, accuracy
- **Environmental factors**: Lighting, weather, occlusions
- **Hardware characteristics**: Noise, drift, calibration errors
- **Integration requirements**: ROS 2 message formats, timing

## Camera Simulation

### RGB Camera with Realistic Parameters

```xml
<!-- Gazebo camera simulation with realistic parameters -->
<gazebo reference="rgb_camera">
  <sensor name="rgb_camera" type="camera">
    <update_rate>30</update_rate>
    <camera name="head_camera">
      <!-- Physical properties matching real camera -->
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

      <!-- Realistic noise model -->
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.007</stddev>  <!-- Match real camera noise characteristics -->
      </noise>
    </camera>

    <always_on>true</always_on>
    <visualize>true</visualize>

    <!-- ROS 2 interface -->
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>camera</namespace>
        <remapping>~/image_raw:=image_color</remapping>
        <remapping>~/camera_info:=camera_info</remapping>
      </ros>
      <camera_name>head_camera</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>camera_optical_frame</frame_name>
      <hack_baseline>0.07</hack_baseline>
      <distortion_k1>0.0</distortion_k1>
      <distortion_k2>0.0</distortion_k2>
      <distortion_k3>0.0</distortion_k3>
      <distortion_t1>0.0</distortion_t1>
      <distortion_t2>0.0</distortion_t2>
    </plugin>
  </sensor>
</gazebo>
```

### Depth Camera Simulation

```xml
<gazebo reference="depth_camera">
  <sensor name="depth_camera" type="depth">
    <update_rate>30</update_rate>
    <camera name="depth_head_camera">
      <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
      <image>
        <width>640</width>
        <height>480</height>
        <format>R16</format>  <!-- 16-bit depth -->
      </image>
      <clip>
        <near>0.1</near>
        <far>5.0</far>
      </clip>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>  <!-- 1cm depth noise -->
      </noise>
    </camera>

    <always_on>true</always_on>
    <visualize>true</visualize>

    <plugin name="depth_camera_controller" filename="libgazebo_ros_openni_kinect.so">
      <ros>
        <namespace>depth_camera</namespace>
        <remapping>~/image_raw:=depth/image_raw</remapping>
        <remapping>~/camera_info:=depth/camera_info</remapping>
        <remapping>~/depth/image_raw:=depth/image_raw</remapping>
        <remapping>~/depth/camera_info:=depth/camera_info</remapping>
      </ros>

      <camera_name>depth_camera</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <depth_image_topic_name>depth/image_raw</depth_image_topic_name>
      <depth_image_camera_info_topic_name>depth/camera_info</depth_image_camera_info_topic_name>
      <point_cloud_topic_name>depth/points</point_cloud_topic_name>
      <frame_name>depth_camera_optical_frame</frame_name>
      <baseline>0.1</baseline>
      <distortion_k1>0.0</distortion_k1>
      <distortion_k2>0.0</distortion_k2>
      <distortion_k3>0.0</distortion_k3>
      <distortion_t1>0.0</distortion_t1>
      <distortion_t2>0.0</distortion_t2>
      <point_cloud_cutoff>0.1</point_cloud_cutoff>
      <point_cloud_cutoff_max>5.0</point_cloud_cutoff_max>
    </plugin>
  </sensor>
</gazebo>
```

## Lidar Simulation

### 2D Lidar with Realistic Noise

```xml
<gazebo reference="lidar_2d">
  <sensor name="laser_2d" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>  <!-- 0.5 degree resolution over 360° -->
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -π -->
          <max_angle>3.14159</max_angle>   <!-- π -->
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>  <!-- 10m range -->
        <resolution>0.01</resolution>  <!-- 1cm resolution -->
      </range>
    </ray>

    <plugin name="laser_2d_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>laser_2d</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>laser_2d_frame</frame_name>

      <!-- Realistic noise parameters -->
      <gaussian_noise>0.01</gaussian_noise>  <!-- 1cm noise -->
      <topic_name>scan</topic_name>
    </plugin>

    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

### 3D Lidar (Velodyne-style)

```xml
<gazebo reference="lidar_3d">
  <sensor name="velodyne_vlp16" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>1800</samples>  <!-- High resolution -->
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -π -->
          <max_angle>3.14159</max_angle>   <!-- π -->
        </horizontal>
        <vertical>
          <samples>16</samples>    <!-- 16 beams -->
          <resolution>1</resolution>
          <min_angle>-0.2618</min_angle>  <!-- -15 degrees -->
          <max_angle>0.2618</max_angle>   <!-- 15 degrees -->
        </vertical>
      </scan>
      <range>
        <min>0.3</min>
        <max>100.0</max>  <!-- 100m range -->
        <resolution>0.001</resolution>  <!-- 1mm resolution -->
      </range>
    </ray>

    <plugin name="velodyne_controller" filename="libgazebo_ros_velodyne_gpu_laser.so">
      <ros>
        <namespace>velodyne</namespace>
        <remapping>~/out:=points</remapping>
      </ros>
      <topic_name>points</topic_name>
      <frame_name>velodyne_frame</frame_name>
      <min_range>0.3</min_range>
      <max_range>100.0</max_range>
      <gaussian_noise>0.008</gaussian_noise>  <!-- 8mm noise -->
    </plugin>

    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

## IMU Simulation

### Realistic IMU with Noise Characteristics

```xml
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>

    <plugin name="imu_controller" filename="libgazebo_ros_imu.so">
      <ros>
        <namespace>imu</namespace>
        <remapping>~/out:=data</remapping>
      </ros>

      <topic_name>data</topic_name>
      <body_name>imu_link</body_name>
      <frame_name>imu_frame</frame_name>
      <initial_orientation_as_reference>false</initial_orientation_as_reference>

      <!-- Realistic IMU noise parameters -->
      <gaussian_noise>0.0017</gaussian_noise>  <!-- ~0.1 deg/s for gyroscope -->

      <!-- Gyroscope noise -->
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>        <!-- 2e-4 rad/s^2 -->
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </noise>
        </z>
      </angular_velocity>

      <!-- Accelerometer noise -->
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>      <!-- 1.7e-2 m/s^2 -->
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </noise>
        </z>
      </linear_acceleration>
    </plugin>
  </sensor>
</gazebo>
```

## Multi-Sensor Fusion Simulation

### Simulating Sensor Arrays

```xml
<!-- Combined sensor setup for humanoid robot head -->
<gazebo reference="head_link">
  <!-- RGB-D camera pair -->
  <sensor name="stereo_left" type="camera">
    <pose>-0.05 0.05 0 0 0 0</pose>  <!-- Left of center -->
    <camera name="left_camera">
      <horizontal_fov>1.047</horizontal_fov>
      <image><width>640</width><height>480</height><format>R8G8B8</format></image>
      <clip><near>0.1</near><far>10.0</far></clip>
    </camera>
    <plugin name="left_camera_controller" filename="libgazebo_ros_camera.so">
      <camera_name>stereo/left</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>stereo_left_optical_frame</frame_name>
    </plugin>
  </sensor>

  <sensor name="stereo_right" type="camera">
    <pose>-0.05 -0.05 0 0 0 0</pose>  <!-- Right of center -->
    <camera name="right_camera">
      <horizontal_fov>1.047</horizontal_fov>
      <image><width>640</width><height>480</height><format>R8G8B8</format></image>
      <clip><near>0.1</near><far>10.0</far></clip>
    </camera>
    <plugin name="right_camera_controller" filename="libgazebo_ros_camera.so">
      <camera_name>stereo/right</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>stereo_right_optical_frame</frame_name>
    </plugin>
  </sensor>

  <!-- IMU in head for orientation -->
  <sensor name="head_imu" type="imu">
    <always_on>true</always_on>
    <update_rate>200</update_rate>
    <plugin name="head_imu_controller" filename="libgazebo_ros_imu.so">
      <topic_name>imu/data</topic_name>
      <body_name>head_link</body_name>
      <frame_name>head_imu_frame</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## Unity Sensor Simulation

### Camera Simulation in Unity

```csharp
using UnityEngine;
using Ros2Unity;
using System.Collections;

public class UnityCameraSimulator : MonoBehaviour
{
    [Header("Camera Configuration")]
    public Camera unityCamera;
    public string topicName = "unity_camera/image_raw";
    public int imageWidth = 640;
    public int imageHeight = 480;
    public int publishRate = 30; // Hz

    [Header("Noise Parameters")]
    public bool enableNoise = true;
    public float noiseIntensity = 0.01f;
    public float noiseFrequency = 10.0f;

    [Header("Distortion Parameters")]
    public bool enableDistortion = false;
    public float distortionK1 = 0.0f;
    public float distortionK2 = 0.0f;
    public float distortionP1 = 0.0f;
    public float distortionP2 = 0.0f;

    private ROS2UnityComponent ros2Unity;
    private Publisher imagePublisher;
    private RenderTexture renderTexture;
    private int frameCount = 0;
    private Texture2D noiseTexture;
    private ComputeShader noiseComputeShader;

    void Start()
    {
        InitializeCameraSimulation();
        InitializeNoiseSystem();
    }

    void InitializeCameraSimulation()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        imagePublisher = ros2Unity.CreatePublisher<sensor_msgs.msg.Image>(topicName);

        // Create render texture for camera output
        renderTexture = new RenderTexture(imageWidth, imageHeight, 24, RenderTextureFormat.ARGB32);
        unityCamera.targetTexture = renderTexture;

        // Configure camera properties to match real specifications
        unityCamera.fieldOfView = 60.0f; // 1.047 radians
    }

    void InitializeNoiseSystem()
    {
        if (enableNoise)
        {
            // Create noise texture
            noiseTexture = new Texture2D(imageWidth, imageHeight, TextureFormat.RGB24, false);
            GenerateNoiseTexture();
        }
    }

    void Update()
    {
        if (frameCount % (60 / publishRate) == 0) // Unity runs at 60 FPS
        {
            PublishCameraImage();
        }
        frameCount = (frameCount + 1) % 60;
    }

    void PublishCameraImage()
    {
        RenderTexture.active = renderTexture;
        Texture2D imageTexture = new Texture2D(renderTexture.width, renderTexture.height,
                                               TextureFormat.RGB24, false);
        imageTexture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        imageTexture.Apply();

        // Apply noise if enabled
        if (enableNoise)
        {
            ApplyNoiseToImage(imageTexture);
        }

        // Apply distortion if enabled
        if (enableDistortion)
        {
            ApplyDistortionToImage(imageTexture);
        }

        // Convert to ROS 2 Image message
        sensor_msgs.msg.Image imageMsg = new sensor_msgs.msg.Image();
        imageMsg.header.stamp = GetROSTimestamp();
        imageMsg.header.frame_id = "unity_camera_optical_frame";
        imageMsg.height = (uint)renderTexture.height;
        imageMsg.width = (uint)renderTexture.width;
        imageMsg.encoding = "rgb8";
        imageMsg.is_bigendian = 0;
        imageMsg.step = (uint)(renderTexture.width * 3); // 3 bytes per pixel
        imageMsg.data = Texture2DToByteArray(imageTexture);

        imagePublisher.Publish(imageMsg);

        DestroyImmediate(imageTexture);
    }

    void ApplyNoiseToImage(Texture2D imageTexture)
    {
        Color[] pixels = imageTexture.GetPixels();

        for (int i = 0; i < pixels.Length; i++)
        {
            // Add Gaussian noise
            float noiseX = Random.Range(-noiseIntensity, noiseIntensity);
            float noiseY = Random.Range(-noiseIntensity, noiseIntensity);
            float noiseZ = Random.Range(-noiseIntensity, noiseIntensity);

            pixels[i] = new Color(
                Mathf.Clamp01(pixels[i].r + noiseX),
                Mathf.Clamp01(pixels[i].g + noiseY),
                Mathf.Clamp01(pixels[i].b + noiseZ)
            );
        }

        imageTexture.SetPixels(pixels);
        imageTexture.Apply();
    }

    void ApplyDistortionToImage(Texture2D imageTexture)
    {
        // Apply simple radial distortion (simplified implementation)
        Color[] originalPixels = imageTexture.GetPixels();
        Color[] distortedPixels = new Color[originalPixels.Length];

        int width = imageTexture.width;
        int height = imageTexture.height;

        // Center of image
        float centerX = width / 2.0f;
        float centerY = height / 2.0f;

        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int index = y * width + x;

                // Normalize coordinates to [-1, 1]
                float normX = (x - centerX) / centerX;
                float normY = (y - centerY) / centerY;

                // Calculate distance from center
                float r = Mathf.Sqrt(normX * normX + normY * normY);

                // Apply distortion coefficients
                float r2 = r * r;
                float r4 = r2 * r2;
                float distortionFactor = 1.0f + distortionK1 * r2 + distortionK2 * r4;

                // Calculate distorted coordinates
                float distortedX = normX * distortionFactor;
                float distortedY = normY * distortionFactor;

                // Convert back to pixel coordinates
                int srcX = Mathf.RoundToInt((distortedX * centerX) + centerX);
                int srcY = Mathf.RoundToInt((distortedY * centerY) + centerY);

                // Bounds checking
                if (srcX >= 0 && srcX < width && srcY >= 0 && srcY < height)
                {
                    int srcIndex = srcY * width + srcX;
                    distortedPixels[index] = originalPixels[srcIndex];
                }
                else
                {
                    distortedPixels[index] = Color.black; // Outside image
                }
            }
        }

        imageTexture.SetPixels(distortedPixels);
        imageTexture.Apply();
    }

    byte[] Texture2DToByteArray(Texture2D texture)
    {
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
        builtin_interfaces.msg.Time time = new builtin_interfaces.msg.Time();
        System.TimeSpan timeSpan = System.DateTime.UtcNow - new System.DateTime(1970, 1, 1);
        time.sec = (int)timeSpan.TotalSeconds;
        time.nanosec = (uint)(timeSpan.Milliseconds * 1000000);
        return time;
    }

    void GenerateNoiseTexture()
    {
        Color[] noisePixels = new Color[noiseTexture.width * noiseTexture.height];

        for (int i = 0; i < noisePixels.Length; i++)
        {
            float noiseValue = Random.Range(-noiseIntensity, noiseIntensity);
            noisePixels[i] = new Color(noiseValue, noiseValue, noiseValue);
        }

        noiseTexture.SetPixels(noisePixels);
        noiseTexture.Apply();
    }

    void OnDestroy()
    {
        if (renderTexture) renderTexture.Release();
        if (noiseTexture) DestroyImmediate(noiseTexture);
    }
}
```

## Sensor Validation and Calibration

### Validation Techniques

```csharp
using UnityEngine;
using System.Collections.Generic;

public class SensorValidator : MonoBehaviour
{
    [Header("Validation Parameters")]
    public float positionTolerance = 0.01f;  // 1cm tolerance
    public float orientationTolerance = 0.017f;  // 1 degree tolerance
    public float velocityTolerance = 0.1f;  // 0.1 m/s tolerance

    [Header("Reference Data")]
    public bool useGroundTruth = true;
    public Transform groundTruthTransform;

    private Dictionary<string, SensorReading> lastReadings = new Dictionary<string, SensorReading>();
    private Dictionary<string, float> validationErrors = new Dictionary<string, float>();

    public class SensorReading
    {
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 velocity;
        public float timestamp;
    }

    public void ValidateSensorReading(string sensorId, SensorReading sensorReading)
    {
        if (!useGroundTruth || groundTruthTransform == null)
        {
            return;
        }

        // Get ground truth values
        Vector3 groundTruthPos = groundTruthTransform.position;
        Quaternion groundTruthRot = groundTruthTransform.rotation;

        // Calculate errors
        float positionError = Vector3.Distance(sensorReading.position, groundTruthPos);
        float orientationError = Quaternion.Angle(sensorReading.rotation, groundTruthRot);

        // Store validation results
        validationErrors[sensorId] = positionError;

        // Log significant errors
        if (positionError > positionTolerance)
        {
            Debug.LogWarning($"Position error for {sensorId}: {positionError:F3}m (threshold: {positionTolerance}m)");
        }

        if (orientationError > orientationTolerance)
        {
            Debug.LogWarning($"Orientation error for {sensorId}: {orientationError:F3}° (threshold: {orientationTolerance * Mathf.Rad2Deg}°)");
        }

        // Update last reading
        lastReadings[sensorId] = sensorReading;
    }

    public float GetValidationScore(string sensorId)
    {
        if (validationErrors.ContainsKey(sensorId))
        {
            // Lower error = higher score
            return Mathf.Clamp01(1.0f - validationErrors[sensorId] / positionTolerance);
        }
        return 1.0f; // No error data = perfect score
    }

    public void ResetValidation()
    {
        lastReadings.Clear();
        validationErrors.Clear();
    }
}
```

## Integration with VLA Systems

Sensor simulation enables:
- **Perception Training**: High-quality synthetic data for vision systems
- **Sensor Fusion**: Testing integration of multiple sensor modalities
- **Localization**: Testing position and orientation estimation
- **Safety Validation**: Ensuring sensors detect hazards appropriately
- **Performance Testing**: Validating sensor processing under various conditions

## Best Practices

1. **Match Real Hardware**: Configure simulation parameters to match real sensor specifications
2. **Realistic Noise**: Include appropriate noise models based on sensor datasheets
3. **Environmental Factors**: Account for lighting, weather, and environmental conditions
4. **Validation**: Regularly validate simulation outputs against real sensor data
5. **Performance**: Optimize sensor simulation for real-time performance
6. **Calibration**: Include sensor calibration parameters in simulation

This comprehensive sensor simulation system provides the realistic sensor data necessary for developing and validating perception-based humanoid robot systems.