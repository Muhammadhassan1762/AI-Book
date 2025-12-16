---
sidebar_position: 2
---

# LiDAR, Depth Cameras, and IMUs

## Realistic Simulation of 3D Perception and Inertial Sensors

LiDAR, depth cameras, and IMUs are fundamental sensors for humanoid robot perception and navigation. This chapter covers the realistic simulation of these sensors, including their physical properties, noise characteristics, and integration with ROS 2 systems for vision-language-action applications.

## Learning Objectives

By the end of this chapter, you will:
- Configure realistic LiDAR simulation with appropriate beam patterns and noise
- Implement depth camera simulation with realistic depth sensing properties
- Set up IMU simulation with realistic noise and bias characteristics
- Validate sensor data quality and accuracy
- Integrate multiple sensors for robust perception systems
- Apply sensor simulation to VLA system development

## LiDAR Simulation

### 2D LiDAR Configuration

```xml
<!-- 2D LiDAR simulation for navigation -->
<gazebo reference="laser_2d_link">
  <sensor name="hokuyo_2d" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>1081</samples>  <!-- High resolution for Hokuyo URG-04LX -->
          <resolution>1</resolution>
          <min_angle>-2.2689</min_angle>  <!-- -130 degrees -->
          <max_angle>2.2689</max_angle>   <!-- 130 degrees -->
        </horizontal>
      </scan>
      <range>
        <min>0.06</min>    <!-- 6cm minimum range -->
        <max>5.6</max>     <!-- 5.6m maximum range -->
        <resolution>0.01</resolution>  <!-- 1cm resolution -->
      </range>
    </ray>

    <plugin name="hokuyo_2d_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>laser</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>laser_2d_frame</frame_name>

      <!-- Realistic noise parameters -->
      <gaussian_noise>0.01</gaussian_noise>  <!-- 1cm noise -->

      <!-- Update rate -->
      <update_rate>10</update_rate>
    </plugin>

    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

### 3D LiDAR Configuration (Velodyne VLP-16)

```xml
<!-- Velodyne VLP-16 3D LiDAR simulation -->
<gazebo reference="velodyne_vlp16">
  <sensor name="velodyne_VLP16" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>1800</samples>  <!-- High horizontal resolution -->
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -π -->
          <max_angle>3.14159</max_angle>   <!-- π -->
        </horizontal>
        <vertical>
          <samples>16</samples>    <!-- 16 vertical beams -->
          <resolution>1</resolution>
          <min_angle>-0.2618</min_angle>  <!-- -15 degrees (lower) -->
          <max_angle>0.1745</max_angle>   <!-- 10 degrees (upper) -->
        </vertical>
      </scan>
      <range>
        <min>0.3</min>      <!-- 0.3m minimum range -->
        <max>120.0</max>    <!-- 120m maximum range -->
        <resolution>0.002</resolution>  <!-- 2mm resolution -->
      </range>
    </ray>

    <plugin name="velodyne_vlp16_controller" filename="libgazebo_ros_velodyne_gpu_laser.so">
      <ros>
        <namespace>velodyne</namespace>
        <remapping>~/out:=points</remapping>
      </ros>
      <topic_name>points</topic_name>
      <frame_name>velodyne_frame</frame_name>

      <!-- Realistic parameters -->
      <min_range>0.3</min_range>
      <max_range>120.0</max_range>
      <gaussian_noise>0.008</gaussian_noise>  <!-- 8mm noise -->
      <update_rate>10</update_rate>
    </plugin>

    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

### Ouster OS1-64 LiDAR Configuration

```xml
<!-- Ouster OS1-64 high-resolution LiDAR -->
<gazebo reference="os1_64_link">
  <sensor name="os1_64" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>1024</samples>  <!-- 1024 horizontal samples -->
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -π -->
          <max_angle>3.14159</max_angle>   <!-- π -->
        </horizontal>
        <vertical>
          <samples>64</samples>    <!-- 64 vertical channels -->
          <resolution>1</resolution>
          <min_angle>-0.5236</min_angle>  <!-- -30 degrees -->
          <max_angle>0.1920</max_angle>   <!-- 11 degrees -->
        </vertical>
      </scan>
      <range>
        <min>0.1</min>      <!-- 0.1m minimum range -->
        <max>120.0</max>    <!-- 120m maximum range -->
        <resolution>0.001</resolution>  <!-- 1mm resolution -->
      </range>
    </ray>

    <plugin name="os1_64_controller" filename="libgazebo_ros_os1_gpu_laser.so">
      <ros>
        <namespace>os1</namespace>
        <remapping>~/out:=points</remapping>
      </ros>
      <topic_name>points</topic_name>
      <frame_name>os1_64_frame</frame_name>

      <!-- Ouster-specific parameters -->
      <min_range>0.1</min_range>
      <max_range>120.0</max_range>
      <gaussian_noise>0.005</gaussian_noise>  <!-- 5mm noise -->
      <update_rate>10</update_rate>
    </plugin>

    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

## Depth Camera Simulation

### Intel RealSense D435 Configuration

```xml
<!-- Intel RealSense D435 depth camera simulation -->
<gazebo reference="camera_depth_frame">
  <sensor name="camera_depth" type="depth">
    <update_rate>30</update_rate>

    <camera name="realsense_d435">
      <horizontal_fov>1.2217</horizontal_fov>  <!-- 70 degrees -->
      <image>
        <width>1280</width>
        <height>720</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>10.0</far>
      </clip>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>  <!-- 1cm depth noise -->
      </noise>
    </camera>

    <always_on>true</always_on>
    <visualize>false</visualize>

    <plugin name="realsense_d435_controller" filename="libgazebo_ros_openni_kinect.so">
      <ros>
        <namespace>camera</namespace>
        <remapping>~/image_raw:=color/image_raw</remapping>
        <remapping>~/camera_info:=color/camera_info</remapping>
        <remapping>~/depth/image_raw:=depth/image_rect_raw</remapping>
        <remapping>~/depth/camera_info:=depth/camera_info</remapping>
        <remapping>~/depth/points:=depth/color/points</remapping>
      </ros>

      <camera_name>camera</camera_name>
      <image_topic_name>color/image_raw</image_topic_name>
      <camera_info_topic_name>color/camera_info</camera_info_topic_name>
      <depth_image_topic_name>depth/image_rect_raw</depth_image_topic_name>
      <depth_image_camera_info_topic_name>depth/camera_info</depth_image_camera_info_topic_name>
      <point_cloud_topic_name>depth/color/points</point_cloud_topic_name>
      <frame_name>camera_depth_optical_frame</frame_name>
      <baseline>0.05</baseline>  <!-- 5cm baseline -->
      <distortion_k1>0.0</distortion_k1>
      <distortion_k2>0.0</distortion_k2>
      <distortion_k3>0.0</distortion_k3>
      <distortion_t1>0.0</distortion_t1>
      <distortion_t2>0.0</distortion_t2>
      <point_cloud_cutoff>0.1</point_cloud_cutoff>  <!-- 10cm min depth -->
      <point_cloud_cutoff_max>10.0</point_cloud_cutoff_max>  <!-- 10m max depth -->
      <Cx_prime>0</Cx_prime>
      <Cx>640.5</Cx>
      <Cy>360.5</Cy>
      <focal_length>640.0</focal_length>  <!-- fx = fy -->
    </plugin>
  </sensor>
</gazebo>
```

### Stereo Camera Configuration

```xml
<!-- Stereo camera setup -->
<gazebo reference="stereo_camera_link">
  <!-- Left camera -->
  <sensor name="stereo_left" type="camera">
    <pose>0 0.05 0 0 0 0</pose>  <!-- 5cm baseline -->
    <camera name="left_camera">
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
        <stddev>0.007</stddev>
      </noise>
    </camera>

    <plugin name="stereo_left_controller" filename="libgazebo_ros_camera.so">
      <camera_name>stereo/left</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>stereo_left_optical_frame</frame_name>
      <robot_namespace>stereo</robot_namespace>
    </plugin>

    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <visualize>false</visualize>
  </sensor>

  <!-- Right camera -->
  <sensor name="stereo_right" type="camera">
    <pose>0 -0.05 0 0 0 0</pose>  <!-- 5cm baseline -->
    <camera name="right_camera">
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
        <stddev>0.007</stddev>
      </noise>
    </camera>

    <plugin name="stereo_right_controller" filename="libgazebo_ros_camera.so">
      <camera_name>stereo/right</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>stereo_right_optical_frame</frame_name>
      <robot_namespace>stereo</robot_namespace>
    </plugin>

    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

## IMU Simulation

### Realistic IMU Configuration

```xml
<!-- High-quality IMU simulation -->
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>200</update_rate>  <!-- 200Hz update rate -->

    <plugin name="imu_controller" filename="libgazebo_ros_imu.so">
      <ros>
        <namespace>imu</namespace>
        <remapping>~/out:=data</remapping>
      </ros>

      <topic_name>data</topic_name>
      <body_name>imu_link</body_name>
      <frame_name>imu_frame</frame_name>
      <initial_orientation_as_reference>false</initial_orientation_as_reference>

      <!-- Realistic noise parameters based on ADIS16448 IMU -->
      <gaussian_noise>0.0017</gaussian_noise>  <!-- ~0.1 deg/s for gyroscope -->

      <!-- Gyroscope noise characteristics -->
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>        <!-- 2e-4 rad/s^2 -->
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
            <dynamic_bias_std>0.0001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
            <dynamic_bias_std>0.0001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
            <dynamic_bias_std>0.0001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
          </noise>
        </z>
      </angular_velocity>

      <!-- Accelerometer noise characteristics -->
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>      <!-- 1.7e-2 m/s^2 -->
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
            <dynamic_bias_std>0.001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
            <dynamic_bias_std>0.001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
            <dynamic_bias_std>0.001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
          </noise>
        </z>
      </linear_acceleration>
    </plugin>
  </sensor>
</gazebo>
```

### Multi-IMU Setup for Redundancy

```xml
<!-- Multiple IMUs for redundancy and calibration -->
<gazebo reference="head_link">
  <!-- Primary IMU in head -->
  <sensor name="primary_imu" type="imu">
    <always_on>true</always_on>
    <update_rate>200</update_rate>
    <pose>0.05 0 0.1 0 0 0</pose>  <!-- Offset from center -->

    <plugin name="primary_imu_controller" filename="libgazebo_ros_imu.so">
      <topic_name>imu/primary</topic_name>
      <body_name>head_link</body_name>
      <frame_name>head_imu_frame</frame_name>
      <gaussian_noise>0.0017</gaussian_noise>
    </plugin>
  </sensor>

  <!-- Secondary IMU in torso -->
  <sensor name="secondary_imu" type="imu">
    <always_on>true</always_on>
    <update_rate>200</update_rate>
    <pose>-0.1 0 0 0 0 0</pose>  <!-- In torso -->

    <plugin name="secondary_imu_controller" filename="libgazebo_ros_imu.so">
      <topic_name>imu/secondary</topic_name>
      <body_name>base_link</body_name>
      <frame_name>torso_imu_frame</frame_name>
      <gaussian_noise>0.0020</gaussian_noise>  <!-- Slightly higher noise -->
    </plugin>
  </sensor>
</gazebo>
```

## Sensor Fusion Simulation

### Combining Multiple Sensors

```xml
<!-- Sensor fusion setup for humanoid robot -->
<gazebo reference="head_link">
  <!-- RGB camera -->
  <sensor name="rgb_camera" type="camera">
    <pose>0 0 0.02 0 0 0</pose>  <!-- Slightly above IMU -->
    <camera name="head_camera">
      <horizontal_fov>1.047</horizontal_fov>
      <image><width>640</width><height>480</height><format>R8G8B8</format></image>
      <clip><near>0.1</near><far>10.0</far></clip>
    </camera>
    <plugin name="rgb_camera_controller" filename="libgazebo_ros_camera.so">
      <camera_name>head_camera</camera_name>
      <frame_name>head_camera_optical_frame</frame_name>
    </plugin>
  </sensor>

  <!-- Depth camera -->
  <sensor name="depth_camera" type="depth">
    <pose>0 0.05 0.02 0 0 0</pose>  <!-- Side-by-side with RGB -->
    <camera name="head_depth">
      <horizontal_fov>1.047</horizontal_fov>
      <image><width>640</width><height>480</height><format>L8</format></image>
      <clip><near>0.1</near><far>10.0</far></clip>
    </camera>
    <plugin name="depth_camera_controller" filename="libgazebo_ros_openni_kinect.so">
      <camera_name>head_depth</camera_name>
      <frame_name>head_depth_optical_frame</frame_name>
    </plugin>
  </sensor>

  <!-- IMU -->
  <sensor name="head_imu" type="imu">
    <pose>0 -0.05 0.02 0 0 0</pose>  <!-- Center position -->
    <plugin name="head_imu_controller" filename="libgazebo_ros_imu.so">
      <topic_name>imu/head</topic_name>
      <frame_name>head_imu_optical_frame</frame_name>
    </plugin>
  </sensor>

  <!-- 2D LiDAR -->
  <sensor name="head_lidar" type="ray">
    <pose>0.02 0 0.05 0 0 0</pose>  <!-- Above other sensors -->
    <ray>
      <scan><horizontal><samples>720</samples><min_angle>-3.14</min_angle><max_angle>3.14</max_angle></horizontal></scan>
      <range><min>0.1</min><max>10.0</max></range>
    </ray>
    <plugin name="head_lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <topic_name>lidar/head_scan</topic_name>
      <frame_name>head_lidar_frame</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## Unity Sensor Simulation

### Depth Camera in Unity

```csharp
using UnityEngine;
using Ros2Unity;
using System.Collections;

public class UnityDepthCameraSimulator : MonoBehaviour
{
    [Header("Camera Configuration")]
    public Camera unityCamera;
    public string colorTopicName = "unity/rgb/image_raw";
    public string depthTopicName = "unity/depth/image_raw";
    public int imageWidth = 640;
    public int imageHeight = 480;
    public int publishRate = 30; // Hz

    [Header("Depth Configuration")]
    public float minDepth = 0.1f;
    public float maxDepth = 10.0f;
    public float depthNoiseStdDev = 0.01f;  // 1cm standard deviation

    [Header("Performance")]
    public bool enableDownsampling = false;
    public int downsamplingFactor = 2;  // Reduce resolution by factor

    private ROS2UnityComponent ros2Unity;
    private Publisher colorPublisher;
    private Publisher depthPublisher;
    private RenderTexture colorTexture;
    private RenderTexture depthTexture;
    private int frameCount = 0;
    private int sequenceNumber = 0;

    void Start()
    {
        InitializeDepthCameraSimulation();
    }

    void InitializeDepthCameraSimulation()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        // Create publishers
        colorPublisher = ros2Unity.CreatePublisher<sensor_msgs.msg.Image>(colorTopicName);
        depthPublisher = ros2Unity.CreatePublisher<sensor_msgs.msg.Image>(depthTopicName);

        // Create render textures
        int effectiveWidth = enableDownsampling ? imageWidth / downsamplingFactor : imageWidth;
        int effectiveHeight = enableDownsampling ? imageHeight / downsamplingFactor : imageHeight;

        colorTexture = new RenderTexture(effectiveWidth, effectiveHeight, 24, RenderTextureFormat.ARGB32);
        colorTexture.Create();
        unityCamera.targetTexture = colorTexture;

        depthTexture = new RenderTexture(effectiveWidth, effectiveHeight, 24, RenderTextureFormat.RFloat);
        depthTexture.Create();
    }

    void Update()
    {
        if (frameCount % (60 / publishRate) == 0) // Unity runs at 60 FPS
        {
            PublishDepthCameraData();
        }
        frameCount = (frameCount + 1) % 60;
    }

    void PublishDepthCameraData()
    {
        // Capture color image
        RenderTexture.active = colorTexture;
        Texture2D colorImage = new Texture2D(colorTexture.width, colorTexture.height, TextureFormat.RGB24, false);
        colorImage.ReadPixels(new Rect(0, 0, colorTexture.width, colorTexture.height), 0, 0);
        colorImage.Apply();

        // Publish color image
        sensor_msgs.msg.Image colorMsg = CreateImageMessage(colorImage, "rgb8");
        colorMsg.header.stamp = GetROSTimestamp();
        colorMsg.header.frame_id = "unity_rgb_camera_optical_frame";
        colorPublisher.Publish(colorMsg);

        // Capture depth image
        RenderTexture.active = depthTexture;
        Texture2D depthImage = new Texture2D(depthTexture.width, depthTexture.height, TextureFormat.RFloat, false);
        depthImage.ReadPixels(new Rect(0, 0, depthTexture.width, depthTexture.height), 0, 0);
        depthImage.Apply();

        // Apply noise to depth image
        ApplyDepthNoise(depthImage);

        // Publish depth image
        sensor_msgs.msg.Image depthMsg = CreateDepthImageMessage(depthImage);
        depthMsg.header.stamp = GetROSTimestamp();
        depthMsg.header.frame_id = "unity_depth_camera_optical_frame";
        depthPublisher.Publish(depthMsg);

        // Cleanup
        DestroyImmediate(colorImage);
        DestroyImmediate(depthImage);

        sequenceNumber++;
    }

    sensor_msgs.msg.Image CreateImageMessage(Texture2D texture, string encoding)
    {
        sensor_msgs.msg.Image imageMsg = new sensor_msgs.msg.Image();
        imageMsg.height = (uint)texture.height;
        imageMsg.width = (uint)texture.width;
        imageMsg.encoding = encoding;
        imageMsg.is_bigendian = 0;
        imageMsg.step = (uint)(texture.width * GetPixelBytes(encoding));

        // Convert texture to byte array
        Color32[] colors = texture.GetPixels32();
        imageMsg.data = new byte[colors.Length * GetPixelBytes(encoding)];

        for (int i = 0; i < colors.Length; i++)
        {
            imageMsg.data[i * 3] = colors[i].r;
            imageMsg.data[i * 3 + 1] = colors[i].g;
            imageMsg.data[i * 3 + 2] = colors[i].b;
        }

        return imageMsg;
    }

    sensor_msgs.msg.Image CreateDepthImageMessage(Texture2D texture)
    {
        sensor_msgs.msg.Image imageMsg = new sensor_msgs.msg.Image();
        imageMsg.height = (uint)texture.height;
        imageMsg.width = (uint)texture.width;
        imageMsg.encoding = "32FC1";  // 32-bit float, single channel
        imageMsg.is_bigendian = 0;
        imageMsg.step = (uint)(texture.width * sizeof(float));  // 4 bytes per float

        // Convert depth texture to float array
        Color[] colors = texture.GetPixels();
        float[] depths = new float[colors.Length];

        for (int i = 0; i < colors.Length; i++)
        {
            // Convert grayscale color value to depth (assuming 0-1 range maps to minDepth-maxDepth)
            float normalizedDepth = colors[i].r;  // Use red channel for depth
            depths[i] = minDepth + (normalizedDepth * (maxDepth - minDepth));
        }

        // Convert float array to byte array
        imageMsg.data = new byte[depths.Length * sizeof(float)];
        for (int i = 0; i < depths.Length; i++)
        {
            byte[] floatBytes = System.BitConverter.GetBytes(depths[i]);
            for (int j = 0; j < 4; j++)
            {
                imageMsg.data[i * 4 + j] = floatBytes[j];
            }
        }

        return imageMsg;
    }

    void ApplyDepthNoise(Texture2D depthTexture)
    {
        Color[] pixels = depthTexture.GetPixels();

        for (int i = 0; i < pixels.Length; i++)
        {
            // Convert grayscale value back to depth
            float depth = pixels[i].r;  // Assuming r=g=b for grayscale

            // Apply Gaussian noise
            float noise = GenerateGaussianNoise(depthNoiseStdDev);
            float noisyDepth = Mathf.Clamp(depth + noise, minDepth, maxDepth);

            // Convert back to grayscale
            float normalizedDepth = (noisyDepth - minDepth) / (maxDepth - minDepth);
            pixels[i] = new Color(normalizedDepth, normalizedDepth, normalizedDepth, 1.0f);
        }

        depthTexture.SetPixels(pixels);
        depthTexture.Apply();
    }

    float GenerateGaussianNoise(float stdDev)
    {
        // Box-Muller transform for Gaussian noise
        float u1 = Random.Range(0.0000001f, 1.0f);  // Avoid log(0)
        float u2 = Random.Range(0.0f, 1.0f);
        float gaussian = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Cos(2.0f * Mathf.PI * u2);
        return gaussian * stdDev;
    }

    int GetPixelBytes(string encoding)
    {
        switch (encoding)
        {
            case "rgb8":
            case "bgr8":
                return 3;
            case "mono8":
                return 1;
            default:
                return 3;  // Default to RGB
        }
    }

    builtin_interfaces.msg.Time GetROSTimestamp()
    {
        builtin_interfaces.msg.Time time = new builtin_interfaces.msg.Time();
        System.TimeSpan timeSpan = System.DateTime.UtcNow - new System.DateTime(1970, 1, 1);
        time.sec = (int)timeSpan.TotalSeconds;
        time.nanosec = (uint)(timeSpan.Milliseconds * 1000000);
        return time;
    }

    void OnDestroy()
    {
        if (colorTexture) colorTexture.Release();
        if (depthTexture) depthTexture.Release();
    }
}
```

### IMU Simulation in Unity

```csharp
using UnityEngine;
using Ros2Unity;
using System.Collections;

public class UnityIMUSimulator : MonoBehaviour
{
    [Header("IMU Configuration")]
    public string topicName = "unity/imu/data";
    public int publishRate = 100; // Hz

    [Header("Noise Parameters")]
    public float gyroNoiseStdDev = 2e-4f;      // rad/s
    public float accelNoiseStdDev = 1.7e-2f;   // m/s^2
    public float gyroBiasStdDev = 0.0000075f;  // rad/s bias
    public float accelBiasStdDev = 0.1f;       // m/s^2 bias

    [Header("Performance")]
    public bool enableDrift = true;
    public float driftRate = 0.0001f;  // bias drift per second

    private ROS2UnityComponent ros2Unity;
    private Publisher imuPublisher;
    private int frameCount = 0;

    // IMU state with bias and drift
    private Vector3 gyroBias = Vector3.zero;
    private Vector3 accelBias = Vector3.zero;
    private Vector3 gyroDrift = Vector3.zero;
    private Vector3 accelDrift = Vector3.zero;

    void Start()
    {
        InitializeIMUSimulation();
    }

    void InitializeIMUSimulation()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
        ros2Unity.Init();

        imuPublisher = ros2Unity.CreatePublisher<sensor_msgs.msg.Imu>(topicName);

        // Initialize biases with realistic values
        InitializeBiases();
    }

    void InitializeBiases()
    {
        // Initialize with small random biases
        gyroBias = new Vector3(
            Random.Range(-gyroBiasStdDev, gyroBiasStdDev),
            Random.Range(-gyroBiasStdDev, gyroBiasStdDev),
            Random.Range(-gyroBiasStdDev, gyroBiasStdDev)
        );

        accelBias = new Vector3(
            Random.Range(-accelBiasStdDev, accelBiasStdDev),
            Random.Range(-accelBiasStdDev, accelBiasStdDev),
            Random.Range(-accelBiasStdDev, accelBiasStdDev)
        );
    }

    void Update()
    {
        if (frameCount % (60 / (publishRate / 1000)) == 0) // Adjust for Unity's 60 FPS
        {
            PublishIMUData();
        }
        frameCount = (frameCount + 1) % 60;

        if (enableDrift)
        {
            UpdateDrift();
        }
    }

    void PublishIMUData()
    {
        sensor_msgs.msg.Imu imuMsg = new sensor_msgs.msg.Imu();

        // Set header
        imuMsg.header.stamp = GetROSTimestamp();
        imuMsg.header.frame_id = "unity_imu_frame";

        // Get true angular velocity and linear acceleration from Unity
        Rigidbody rb = GetComponent<Rigidbody>();
        Vector3 trueAngularVel = rb ? rb.angularVelocity : Vector3.zero;
        Vector3 trueLinearAccel = rb ? rb.velocity / Time.fixedDeltaTime : Vector3.zero;

        // Apply gravity compensation to linear acceleration
        trueLinearAccel -= Physics.gravity;

        // Add noise and bias
        Vector3 noisyAngularVel = AddNoiseAndBias(trueAngularVel, gyroBias, gyroNoiseStdDev);
        Vector3 noisyLinearAccel = AddNoiseAndBias(trueLinearAccel, accelBias, accelNoiseStdDev);

        // Convert to ROS format (Unity: left-handed, ROS: right-handed)
        imuMsg.angular_velocity.x = noisyAngularVel.x;
        imuMsg.angular_velocity.y = noisyAngularVel.z;  // Swap Y and Z
        imuMsg.angular_velocity.z = noisyAngularVel.y;

        imuMsg.linear_acceleration.x = noisyLinearAccel.x;
        imuMsg.linear_acceleration.y = noisyLinearAccel.z;  // Swap Y and Z
        imuMsg.linear_acceleration.z = noisyLinearAccel.y;

        // For orientation, we'll use the Unity transform (simplified)
        // In real implementation, this would come from integration of angular velocity
        Quaternion unityRotation = transform.rotation;
        imuMsg.orientation.x = unityRotation.x;
        imuMsg.orientation.y = unityRotation.z;  // Swap Y and Z
        imuMsg.orientation.z = unityRotation.y;
        imuMsg.orientation.w = unityRotation.w;

        // Set covariance matrices (diagonal only for simplicity)
        for (int i = 0; i < 9; i++)
        {
            imuMsg.angular_velocity_covariance[i] = i % 4 == 0 ? gyroNoiseStdDev * gyroNoiseStdDev : 0.0;  // Diagonal
            imuMsg.linear_acceleration_covariance[i] = i % 4 == 0 ? accelNoiseStdDev * accelNoiseStdDev : 0.0;  // Diagonal
        }

        imuPublisher.Publish(imuMsg);
    }

    Vector3 AddNoiseAndBias(Vector3 trueValue, Vector3 bias, float noiseStdDev)
    {
        Vector3 noise = new Vector3(
            GenerateGaussianNoise(noiseStdDev),
            GenerateGaussianNoise(noiseStdDev),
            GenerateGaussianNoise(noiseStdDev)
        );

        return trueValue + bias + noise;
    }

    float GenerateGaussianNoise(float stdDev)
    {
        // Box-Muller transform for Gaussian noise
        float u1 = Random.Range(0.0000001f, 1.0f);
        float u2 = Random.Range(0.0f, 1.0f);
        float gaussian = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Cos(2.0f * Mathf.PI * u2);
        return gaussian * stdDev;
    }

    void UpdateDrift()
    {
        // Simulate slow bias drift
        gyroDrift += new Vector3(
            Random.Range(-driftRate, driftRate) * Time.deltaTime,
            Random.Range(-driftRate, driftRate) * Time.deltaTime,
            Random.Range(-driftRate, driftRate) * Time.deltaTime
        );

        accelDrift += new Vector3(
            Random.Range(-driftRate, driftRate) * Time.deltaTime,
            Random.Range(-driftRate, driftRate) * Time.deltaTime,
            Random.Range(-driftRate, driftRate) * Time.deltaTime
        );

        // Apply drift to biases
        gyroBias += gyroDrift * Time.deltaTime;
        accelBias += accelDrift * Time.deltaTime;
    }

    builtin_interfaces.msg.Time GetROSTimestamp()
    {
        builtin_interfaces.msg.Time time = new builtin_interfaces.msg.Time();
        System.TimeSpan timeSpan = System.DateTime.UtcNow - new System.DateTime(1970, 1, 1);
        time.sec = (int)timeSpan.TotalSeconds;
        time.nanosec = (uint)(timeSpan.Milliseconds * 1000000);
        return time;
    }
}
```

## Sensor Validation

### Validation Techniques

```csharp
using UnityEngine;
using System.Collections.Generic;

public class SensorValidator : MonoBehaviour
{
    [Header("Validation Parameters")]
    public float lidarRangeTolerance = 0.05f;  // 5cm tolerance
    public float depthAccuracyTolerance = 0.02f;  // 2cm tolerance
    public float imuAngularTolerance = 0.017f;  // 1 degree tolerance
    public float imuLinearTolerance = 0.05f;    // 5cm/s tolerance

    [Header("Ground Truth")]
    public bool useGroundTruth = true;
    public Transform groundTruthTransform;

    private Dictionary<string, SensorData> groundTruthData = new Dictionary<string, SensorData>();
    private Dictionary<string, SensorData> simulatedData = new Dictionary<string, SensorData>();

    [System.Serializable]
    public class SensorData
    {
        public Vector3 position;
        public Vector3 linearVelocity;
        public Vector3 angularVelocity;
        public float timestamp;
        public float[] lidarRanges;
        public Texture2D depthImage;
        public float[] depthValues;
    }

    public void ValidateLidarData(string sensorId, float[] simulatedRanges, float[] groundTruthRanges)
    {
        if (groundTruthRanges == null || simulatedRanges == null ||
            groundTruthRanges.Length != simulatedRanges.Length)
        {
            Debug.LogError("Invalid LiDAR data for validation");
            return;
        }

        float totalError = 0f;
        int validPoints = 0;

        for (int i = 0; i < simulatedRanges.Length; i++)
        {
            if (simulatedRanges[i] > 0 && groundTruthRanges[i] > 0)
            {
                float error = Mathf.Abs(simulatedRanges[i] - groundTruthRanges[i]);
                if (error > lidarRangeTolerance)
                {
                    Debug.LogWarning($"LiDAR range error at beam {i}: {error:F3}m (tolerance: {lidarRangeTolerance}m)");
                }
                totalError += error;
                validPoints++;
            }
        }

        float averageError = validPoints > 0 ? totalError / validPoints : float.PositiveInfinity;
        float accuracyPercentage = validPoints > 0 ?
            (float)System.Linq.Enumerable.Count(simulatedRanges, r => Mathf.Abs(r - groundTruthRanges[System.Array.IndexOf(simulatedRanges, r)]) <= lidarRangeTolerance) /
            simulatedRanges.Length * 100 : 0;

        Debug.Log($"LiDAR {sensorId} - Average error: {averageError:F3}m, Accuracy: {accuracyPercentage:F1}%");
    }

    public void ValidateDepthData(Texture2D simulatedDepth, Texture2D groundTruthDepth)
    {
        if (simulatedDepth == null || groundTruthDepth == null ||
            simulatedDepth.width != groundTruthDepth.width ||
            simulatedDepth.height != groundTruthDepth.height)
        {
            Debug.LogError("Invalid depth data for validation");
            return;
        }

        Color[] simPixels = simulatedDepth.GetPixels();
        Color[] gtPixels = groundTruthDepth.GetPixels();

        float totalError = 0f;
        int validPixels = 0;

        for (int i = 0; i < simPixels.Length; i++)
        {
            float simDepth = simPixels[i].r;  // Assuming grayscale depth
            float gtDepth = gtPixels[i].r;

            if (simDepth > 0 && gtDepth > 0)  // Valid depth values
            {
                float error = Mathf.Abs(simDepth - gtDepth);
                if (error > depthAccuracyTolerance)
                {
                    Debug.LogWarning($"Depth error at pixel {i}: {error:F3}m (tolerance: {depthAccuracyTolerance}m)");
                }
                totalError += error;
                validPixels++;
            }
        }

        float averageError = validPixels > 0 ? totalError / validPixels : float.PositiveInfinity;
        Debug.Log($"Depth validation - Average error: {averageError:F3}m over {validPixels} pixels");
    }

    public void ValidateIMUData(Vector3 simulatedAngVel, Vector3 groundTruthAngVel,
                               Vector3 simulatedLinAccel, Vector3 groundTruthLinAccel)
    {
        // Validate angular velocity
        float angVelError = Vector3.Distance(simulatedAngVel, groundTruthAngVel);
        if (angVelError > imuAngularTolerance)
        {
            Debug.LogWarning($"IMU angular velocity error: {angVelError:F3} rad/s (tolerance: {imuAngularTolerance:F3})");
        }

        // Validate linear acceleration
        float linAccelError = Vector3.Distance(simulatedLinAccel, groundTruthLinAccel);
        if (linAccelError > imuLinearTolerance)
        {
            Debug.LogWarning($"IMU linear acceleration error: {linAccelError:F3} m/s² (tolerance: {imuLinearTolerance:F3})");
        }

        Debug.Log($"IMU validation - Angular vel error: {angVelError:F4}, Linear accel error: {linAccelError:F4}");
    }

    public float CalculateLidarAccuracy(float[] simulated, float[] groundTruth, float tolerance)
    {
        if (simulated.Length != groundTruth.Length) return 0f;

        int accuratePoints = 0;
        int totalPoints = 0;

        for (int i = 0; i < simulated.Length; i++)
        {
            if (simulated[i] > 0 && groundTruth[i] > 0)
            {
                if (Mathf.Abs(simulated[i] - groundTruth[i]) <= tolerance)
                {
                    accuratePoints++;
                }
                totalPoints++;
            }
        }

        return totalPoints > 0 ? (float)accuratePoints / totalPoints * 100f : 0f;
    }
}
```

## Integration with VLA Systems

These sensor simulations enable:
- **Perception Training**: High-quality synthetic data for vision systems
- **SLAM Validation**: Testing simultaneous localization and mapping algorithms
- **Navigation Testing**: Validating path planning with realistic sensor data
- **Safety Systems**: Testing obstacle detection and avoidance
- **Human Interaction**: Validating gesture and object recognition

## Best Practices

1. **Match Real Hardware**: Configure simulation parameters to match real sensor specifications
2. **Realistic Noise**: Include appropriate noise models based on sensor datasheets
3. **Environmental Factors**: Account for lighting, weather, and environmental conditions
4. **Validation**: Regularly validate simulation outputs against real sensor data
5. **Performance**: Optimize sensor simulation for real-time performance
6. **Calibration**: Include sensor calibration parameters in simulation
7. **Multi-sensor Fusion**: Test integration of multiple sensor modalities
8. **Edge Cases**: Test sensor behavior under extreme conditions

This comprehensive sensor simulation system provides the realistic sensor data necessary for developing and validating perception-based humanoid robot systems with vision-language-action capabilities.