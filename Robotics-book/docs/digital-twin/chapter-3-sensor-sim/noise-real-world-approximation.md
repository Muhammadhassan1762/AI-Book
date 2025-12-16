---
sidebar_position: 3
---

# Noise and Real-World Approximation

## Modeling Sensor Imperfections for Realistic Simulation

Real-world sensors are imperfect, with various types of noise, biases, and distortions that affect perception and control. This chapter covers the modeling of these imperfections in simulation to create more realistic and robust humanoid robot systems.

## Learning Objectives

By the end of this chapter, you will:
- Understand different types of sensor noise and their origins
- Model realistic noise characteristics for various sensor types
- Implement bias and drift models for long-term accuracy
- Apply environmental factors that affect sensor performance
- Validate noise models against real sensor data
- Design robust perception systems that handle sensor imperfections

## Types of Sensor Noise

### Gaussian Noise
The most common noise model, representing random fluctuations around true values:

```xml
<!-- Gaussian noise in camera simulation -->
<camera name="rgb_camera">
  <noise>
    <type>gaussian</type>
    <mean>0.0</mean>
    <stddev>0.007</stddev>  <!-- 0.7% of signal -->
  </noise>
</camera>

<!-- Gaussian noise in LiDAR simulation -->
<ray>
  <range>
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.01</stddev>  <!-- 1cm noise -->
    </noise>
  </range>
</ray>
```

### Bias and Drift Models

```xml
<!-- IMU with bias and drift -->
<sensor name="imu_sensor" type="imu">
  <angular_velocity>
    <x>
      <noise type="gaussian">
        <mean>0.0</mean>
        <stddev>2e-4</stddev>
        <bias_mean>0.0000075</bias_mean>  <!-- Static bias -->
        <bias_stddev>0.0000008</bias_stddev>

        <!-- Dynamic drift -->
        <dynamic_bias_std>0.0001</dynamic_bias_std>
        <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>
      </noise>
    </x>
  </angular_velocity>
</sensor>
```

### Systematic Errors

```xml
<!-- Camera distortion modeling -->
<camera name="distorted_camera">
  <distortion>
    <k1>0.1</k1>  <!-- Radial distortion coefficient -->
    <k2>-0.05</k2>
    <k3>0.01</k3>
    <p1>0.001</p1>  <!-- Tangential distortion -->
    <p2>-0.002</p2>
  </distortion>
</camera>
```

## Noise Modeling in Gazebo

### Realistic Camera Noise Configuration

```xml
<gazebo reference="camera_link">
  <sensor name="realistic_camera" type="camera">
    <camera name="high_quality_camera">
      <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
      <image>
        <width>1280</width>
        <height>720</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>10.0</far>
      </clip>

      <!-- Complex noise model -->
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.005</stddev>  <!-- Base noise level -->

        <!-- Pixel-dependent noise -->
        <random_distribution>uniform</random_distribution>

        <!-- Temporal noise correlation -->
        <temporal_correlation>0.1</temporal_correlation>
      </noise>
    </camera>

    <plugin name="realistic_camera_controller" filename="libgazebo_ros_camera.so">
      <camera_name>realistic_camera</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>camera_optical_frame</frame_name>

      <!-- Exposure time modeling -->
      <min_exposure_time>0.001</min_exposure_time>  <!-- 1ms -->
      <max_exposure_time>0.1</max_exposure_time>     <!-- 100ms -->

      <!-- Gain modeling -->
      <min_gain>1.0</min_gain>
      <max_gain>10.0</max_gain>
    </plugin>

    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

### LiDAR Noise with Environmental Factors

```xml
<gazebo reference="lidar_link">
  <sensor name="environmental_lidar" type="ray">
    <ray>
      <scan>
        <horizontal>
          <samples>1081</samples>
          <resolution>1</resolution>
          <min_angle>-2.2689</min_angle>
          <max_angle>2.2689</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.06</min>
        <max>5.6</max>
        <resolution>0.01</resolution>

        <!-- Range-dependent noise -->
        <noise>
          <type>gaussian</type>
          <mean>0.0</mean>
          <stddev>0.01</stddev>  <!-- Base noise -->

          <!-- Noise increases with range -->
          <range_dependent_noise>true</range_dependent_noise>
          <noise_coefficient>0.001</noise_coefficient>  <!-- 1mm per meter -->
        </noise>
      </range>
    </ray>

    <plugin name="environmental_lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>lidar</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_frame</frame_name>

      <!-- Environmental effects -->
      <atmospheric_attenuation>0.001</atmospheric_attenuation>  <!-- Signal loss over distance -->
      <multipath_interference>0.005</multipath_interference>    <!-- Ghost returns -->

      <!-- Temperature effects -->
      <temperature_drift>0.0001</temperature_drift>  <!-- Range shift per degree C -->
      <temperature_coefficient>0.01</temperature_coefficient>  <!-- Noise increase with temp -->
    </plugin>

    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
  </sensor>
</gazebo>
```

### IMU with Comprehensive Noise Model

```xml
<gazebo reference="imu_link">
  <sensor name="comprehensive_imu" type="imu">
    <always_on>true</always_on>
    <update_rate>200</update_rate>

    <plugin name="comprehensive_imu_controller" filename="libgazebo_ros_imu.so">
      <ros>
        <namespace>imu</namespace>
        <remapping>~/out:=data</remapping>
      </ros>
      <topic_name>data</topic_name>
      <body_name>imu_link</body_name>
      <frame_name>imu_frame</frame_name>

      <!-- Comprehensive noise model -->
      <gaussian_noise>0.0017</gaussian_noise>

      <!-- Gyroscope noise with all components -->
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <!-- Measurement noise -->
            <mean>0.0</mean>
            <stddev>2e-4</stddev>

            <!-- Static bias -->
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>

            <!-- Dynamic bias (random walk) -->
            <dynamic_bias_std>0.0001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>

            <!-- Scale factor error -->
            <scale_factor_error>0.001</scale_factor_error>

            <!-- Cross-axis sensitivity -->
            <cross_axis_sensitivity>0.001</cross_axis_sensitivity>
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

      <!-- Accelerometer noise -->
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>  <!-- 1.7e-2 m/s² -->

            <!-- Accelerometer-specific errors -->
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
            <dynamic_bias_std>0.001</dynamic_bias_std>
            <dynamic_bias_correlation_time>100</dynamic_bias_correlation_time>

            <!-- Scale factor and misalignment -->
            <scale_factor_error>0.002</scale_factor_error>
            <misalignment>0.001</misalignment>
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

      <!-- Temperature effects -->
      <temperature_sensitivity>
        <gyro_temp_coeff>0.0001</gyro_temp_coeff>  <!-- deg/s per °C -->
        <accel_temp_coeff>0.00001</accel_temp_coeff>  <!-- m/s² per °C -->
        <reference_temperature>25.0</reference_temperature>
      </temperature_sensitivity>

      <!-- Vibration sensitivity -->
      <vibration_sensitivity>
        <gyro_vibration_coeff>0.0001</gyro_vibration_coeff>  <!-- deg/s per g vibration -->
        <accel_vibration_coeff>0.001</accel_vibration_coeff>  <!-- m/s² per g vibration -->
      </vibration_sensitivity>
    </plugin>
  </sensor>
</gazebo>
```

## Environmental Effects Simulation

### Weather and Lighting Conditions

```xml
<!-- Environment-specific sensor behavior -->
<world name="weather_simulated_world">
  <include>
    <uri>model://sun</uri>
  </include>

  <!-- Atmospheric conditions -->
  <atmosphere type="adiabatic">
    <temperature>288.15</temperature>  <!-- Kelvin -->
    <pressure>101325</pressure>        <!-- Pascals -->
    <humidity>0.5</humidity>           <!-- 50% humidity -->
  </atmosphere>

  <!-- Weather effects -->
  <physics type="ode">
    <max_step_size>0.001</max_step_size>
    <real_time_factor>1.0</real_time_factor>

    <!-- Wind effects on sensors -->
    <wind>
      <linear_velocity>0.5 0 0</linear_velocity>  <!-- 0.5 m/s wind -->
      <turbulence>
        <scale>0.1</scale>
        <intensity>0.01</intensity>
      </turbulence>
    </wind>
  </physics>

  <!-- Lighting variations -->
  <light name="sun" type="directional">
    <pose>0 0 10 0 -0.5 0</pose>
    <diffuse>0.8 0.8 0.8 1</diffuse>
    <attenuation>
      <range>100</range>
      <linear>0.01</linear>
      <quadratic>0.001</quadratic>
    </attenuation>
    <direction>-0.3 -0.3 -0.9</direction>
  </light>
</world>
```

### Dynamic Environmental Effects

```csharp
using UnityEngine;
using System.Collections;

public class DynamicEnvironmentEffects : MonoBehaviour
{
    [Header("Environmental Parameters")]
    public float baseTemperature = 25.0f;  // Celsius
    public float temperatureVariation = 10.0f;  // ±10°C
    public float humidityLevel = 0.5f;  // 0-1
    public float windSpeed = 0.0f;  // m/s
    public float lightingVariation = 0.1f;  // 10% variation

    [Header("Effect Multipliers")]
    public float tempNoiseMultiplier = 0.001f;  // Noise increase per °C
    public float humidityNoiseMultiplier = 0.0005f;  // Noise increase per humidity %
    public float windNoiseMultiplier = 0.001f;  // Noise increase per m/s wind

    private float currentTime = 0f;
    private float currentTemperature = 25.0f;
    private float currentHumidity = 0.5f;
    private Vector3 currentWindDirection = Vector3.zero;

    void Start()
    {
        StartCoroutine(UpdateEnvironmentalEffects());
    }

    IEnumerator UpdateEnvironmentalEffects()
    {
        while (true)
        {
            UpdateEnvironment();
            yield return new WaitForSeconds(1.0f);  // Update every second
        }
    }

    void UpdateEnvironment()
    {
        // Update temperature with daily cycle
        float timeOfDay = (currentTime % 86400) / 86400f;  // 24-hour cycle
        float dailyTempVariation = Mathf.Sin(timeOfDay * 2 * Mathf.PI) * temperatureVariation;
        currentTemperature = baseTemperature + dailyTempVariation;

        // Update humidity with random fluctuations
        currentHumidity = Mathf.Clamp01(humidityLevel + Random.Range(-0.1f, 0.1f));

        // Update wind with turbulence
        currentWindDirection = new Vector3(
            Random.Range(-1f, 1f) * windSpeed,
            Random.Range(-0.1f, 0.1f) * windSpeed,
            Random.Range(-1f, 1f) * windSpeed
        ).normalized * windSpeed;

        // Update lighting conditions
        float lightingFactor = 1.0f + Mathf.Sin(timeOfDay * 4 * Mathf.PI) * lightingVariation;

        currentTime += 1.0f;
    }

    public float CalculateEnvironmentalNoiseFactor()
    {
        // Calculate combined environmental effect on sensor noise
        float tempEffect = Mathf.Abs(currentTemperature - baseTemperature) * tempNoiseMultiplier;
        float humidityEffect = currentHumidity * humidityNoiseMultiplier;
        float windEffect = windSpeed * windNoiseMultiplier;

        return 1.0f + tempEffect + humidityEffect + windEffect;
    }

    public float GetTemperatureOffset()
    {
        return currentTemperature - baseTemperature;
    }

    public float GetHumidityLevel()
    {
        return currentHumidity;
    }

    public Vector3 GetWindVector()
    {
        return currentWindDirection;
    }
}
```

## Advanced Noise Models

### Colored Noise and Correlations

```csharp
using UnityEngine;
using System.Collections.Generic;

public class AdvancedNoiseModel : MonoBehaviour
{
    [Header("Noise Parameters")]
    public float whiteNoiseStdDev = 0.01f;
    public float pinkNoiseAlpha = 1.0f;  // 1/f noise exponent
    public float correlationTime = 1.0f;  // Correlation time constant
    public float samplingRate = 100.0f;  // Hz

    private Queue<float> pinkNoiseBuffer = new Queue<float>();
    private const int PINK_NOISE_BUFFER_SIZE = 1000;
    private float[] noiseCoefficients;
    private float[] noiseHistory;
    private System.Random random = new System.Random();

    void Start()
    {
        InitializeAdvancedNoise();
    }

    void InitializeAdvancedNoise()
    {
        // Initialize pink noise coefficients
        InitializePinkNoiseCoefficients();

        // Initialize noise history buffer
        noiseHistory = new float[(int)(samplingRate * correlationTime * 2)];
    }

    void InitializePinkNoiseCoefficients()
    {
        // Generate coefficients for colored noise generation
        noiseCoefficients = new float[PINK_NOISE_BUFFER_SIZE];

        for (int i = 0; i < PINK_NOISE_BUFFER_SIZE; i++)
        {
            // 1/f^alpha noise characteristic
            float frequency = (float)(i + 1) / PINK_NOISE_BUFFER_SIZE;
            noiseCoefficients[i] = Mathf.Pow(frequency, -pinkNoiseAlpha / 2.0f);
        }
    }

    public float GenerateWhiteNoise()
    {
        // Standard Gaussian white noise
        float u1 = (float)random.NextDouble();
        float u2 = (float)random.NextDouble();
        float gaussian = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Cos(2.0f * Mathf.PI * u2);
        return gaussian * whiteNoiseStdDev;
    }

    public float GeneratePinkNoise()
    {
        // Generate pink noise (1/f noise)
        float sum = 0f;
        float normalization = 0f;

        for (int i = 0; i < noiseCoefficients.Length; i++)
        {
            float whiteSample = GenerateWhiteNoise();
            float pinkSample = whiteSample * noiseCoefficients[i];
            sum += pinkSample;
            normalization += noiseCoefficients[i];
        }

        return sum / normalization;
    }

    public float GenerateCorrelatedNoise(float previousValue, float correlationFactor = 0.9f)
    {
        // Generate temporally correlated noise
        float whiteNoise = GenerateWhiteNoise();
        float correlatedValue = correlationFactor * previousValue + (1 - correlationFactor) * whiteNoise;
        return correlatedValue;
    }

    public float GenerateNoiseWithEnvironmentalFactors(float baseNoise, DynamicEnvironmentEffects envEffects)
    {
        // Apply environmental effects to base noise
        float envFactor = envEffects.CalculateEnvironmentalNoiseFactor();
        return baseNoise * envFactor;
    }

    public float[] GenerateColoredNoiseArray(int length, string noiseType = "white")
    {
        float[] noiseArray = new float[length];

        switch (noiseType)
        {
            case "white":
                for (int i = 0; i < length; i++)
                {
                    noiseArray[i] = GenerateWhiteNoise();
                }
                break;

            case "pink":
                for (int i = 0; i < length; i++)
                {
                    noiseArray[i] = GeneratePinkNoise();
                }
                break;

            case "correlated":
                float prevValue = 0f;
                for (int i = 0; i < length; i++)
                {
                    prevValue = GenerateCorrelatedNoise(prevValue);
                    noiseArray[i] = prevValue;
                }
                break;

            default:
                for (int i = 0; i < length; i++)
                {
                    noiseArray[i] = GenerateWhiteNoise();
                }
                break;
        }

        return noiseArray;
    }
}
```

## Unity Sensor Noise Implementation

### Camera Noise with Environmental Effects

```csharp
using UnityEngine;
using System.Collections;

public class UnityCameraNoiseSimulator : MonoBehaviour
{
    [Header("Camera Noise Configuration")]
    public Camera unityCamera;
    public bool enableNoise = true;
    public bool enableEnvironmentalEffects = true;
    public float baseNoiseStdDev = 0.01f;
    public float thermalNoiseCoefficient = 0.0001f;  // Noise per °C
    public float lightingNoiseCoefficient = 0.0005f;  // Noise per lux variation

    [Header("Noise Types")]
    public bool enableWhiteNoise = true;
    public bool enableTemporalCorrelation = true;
    public bool enableSpatialCorrelation = false;

    [Header("Performance")]
    public bool enableDownsampling = true;
    public int downsamplingFactor = 2;

    private AdvancedNoiseModel noiseModel;
    private DynamicEnvironmentEffects envEffects;
    private RenderTexture renderTexture;
    private Texture2D noiseTexture;
    private int imageWidth = 640;
    private int imageHeight = 480;

    void Start()
    {
        InitializeCameraNoiseSimulation();
    }

    void InitializeCameraNoiseSimulation()
    {
        noiseModel = GetComponent<AdvancedNoiseModel>() ?? gameObject.AddComponent<AdvancedNoiseModel>();
        envEffects = FindObjectOfType<DynamicEnvironmentEffects>();

        // Get camera dimensions
        imageWidth = enableDownsampling ? imageWidth / downsamplingFactor : imageWidth;
        imageHeight = enableDownsampling ? imageHeight / downsamplingFactor : imageHeight;

        // Create render texture
        renderTexture = new RenderTexture(imageWidth, imageHeight, 24, RenderTextureFormat.ARGB32);
        unityCamera.targetTexture = renderTexture;

        // Create noise texture
        noiseTexture = new Texture2D(imageWidth, imageHeight, TextureFormat.RGB24, false);
    }

    void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        if (enableNoise)
        {
            ApplyNoiseToImage(source, destination);
        }
        else
        {
            Graphics.Blit(source, destination);
        }
    }

    void ApplyNoiseToImage(RenderTexture source, RenderTexture destination)
    {
        // Capture the current image
        RenderTexture.active = source;
        Texture2D sourceImage = new Texture2D(source.width, source.height, TextureFormat.RGB24, false);
        sourceImage.ReadPixels(new Rect(0, 0, source.width, source.height), 0, 0);
        sourceImage.Apply();

        // Apply noise
        Color[] pixels = sourceImage.GetPixels();

        for (int i = 0; i < pixels.Length; i++)
        {
            // Calculate environmental noise factor
            float envFactor = 1.0f;
            if (enableEnvironmentalEffects && envEffects != null)
            {
                envFactor = envEffects.CalculateEnvironmentalNoiseFactor();
            }

            // Calculate base noise with environmental effects
            float baseNoise = baseNoiseStdDev * envFactor;

            // Apply thermal noise if environment effects are enabled
            if (enableEnvironmentalEffects && envEffects != null)
            {
                float tempOffset = envEffects.GetTemperatureOffset();
                baseNoise += Mathf.Abs(tempOffset) * thermalNoiseCoefficient;
            }

            // Generate noise for each color channel
            float noiseR = GenerateChannelNoise(i, 0, baseNoise);
            float noiseG = GenerateChannelNoise(i, 1, baseNoise);
            float noiseB = GenerateChannelNoise(i, 2, baseNoise);

            // Apply noise to pixel
            pixels[i] = new Color(
                Mathf.Clamp01(pixels[i].r + noiseR),
                Mathf.Clamp01(pixels[i].g + noiseG),
                Mathf.Clamp01(pixels[i].b + noiseB),
                pixels[i].a
            );
        }

        sourceImage.SetPixels(pixels);
        sourceImage.Apply();

        // Write back to destination
        Graphics.Blit(sourceImage, destination);

        // Cleanup
        DestroyImmediate(sourceImage);
    }

    float GenerateChannelNoise(int pixelIndex, int channel, float baseStdDev)
    {
        float noiseValue = 0f;

        if (enableWhiteNoise)
        {
            // Generate white Gaussian noise
            float u1 = Random.value > 0.0000001f ? Random.value : 0.0000001f;  // Avoid log(0)
            float u2 = Random.value;
            float gaussian = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Cos(2.0f * Mathf.PI * u2);
            noiseValue = gaussian * baseStdDev;
        }

        if (enableTemporalCorrelation)
        {
            // Add temporal correlation using previous frame's noise
            // This would require storing previous frame's noise values
            // For simplicity, we'll add some temporal correlation
            float temporalFactor = Mathf.Sin(Time.time * 0.1f) * 0.1f;  // Slow variation
            noiseValue += temporalFactor * baseStdDev;
        }

        if (enableSpatialCorrelation)
        {
            // Add spatial correlation (simplified - real implementation would be more complex)
            int x = pixelIndex % imageWidth;
            int y = pixelIndex / imageWidth;
            float spatialFactor = Mathf.Sin(x * 0.01f) * Mathf.Cos(y * 0.01f) * 0.05f;
            noiseValue += spatialFactor * baseStdDev;
        }

        return noiseValue;
    }

    public void UpdateCameraNoiseParameters(float newNoiseStdDev, float newThermalCoeff, float newLightingCoeff)
    {
        baseNoiseStdDev = newNoiseStdDev;
        thermalNoiseCoefficient = newThermalCoeff;
        lightingNoiseCoefficient = newLightingCoeff;
    }

    void OnDestroy()
    {
        if (renderTexture) renderTexture.Release();
        if (noiseTexture) DestroyImmediate(noiseTexture);
    }
}
```

### LiDAR Noise with Range-Dependent Characteristics

```csharp
using UnityEngine;
using System.Collections.Generic;

public class UnityLiDARNoiseSimulator : MonoBehaviour
{
    [Header("LiDAR Noise Configuration")]
    public float baseRangeNoise = 0.01f;  // 1cm base noise
    public float rangeDependentNoise = 0.001f;  // 1mm per meter
    public float angularNoise = 0.001f;  // 1mrad angular noise
    public float intensityNoise = 0.05f;  // 5% intensity noise
    public float beamDivergence = 0.003f;  // 3mrad beam divergence

    [Header("Environmental Effects")]
    public float atmosphericAttenuation = 0.001f;  // Signal loss per meter
    public float multipathFactor = 0.005f;  // Multipath interference
    public float weatherVisibility = 1.0f;  // 0-1, affects range accuracy

    [Header("Performance")]
    public int maxBeams = 1081;  // Typical for Hokuyo URG-04LX
    public float fovHorizontal = 240f;  // Degrees
    public float fovVertical = 1f;  // Narrow vertical FOV

    private AdvancedNoiseModel noiseModel;
    private DynamicEnvironmentEffects envEffects;
    private float[] beamAngles;
    private float[] lastRangeReadings;

    void Start()
    {
        InitializeLiDARNoiseSimulation();
    }

    void InitializeLiDARNoiseSimulation()
    {
        noiseModel = GetComponent<AdvancedNoiseModel>() ?? gameObject.AddComponent<AdvancedNoiseModel>();
        envEffects = FindObjectOfType<DynamicEnvironmentEffects>();

        // Precompute beam angles
        beamAngles = new float[maxBeams];
        float angleStep = (fovHorizontal * Mathf.Deg2Rad) / (maxBeams - 1);
        for (int i = 0; i < maxBeams; i++)
        {
            beamAngles[i] = (i - maxBeams / 2) * angleStep;
        }

        lastRangeReadings = new float[maxBeams];
    }

    public float[] SimulateLiDARScan(Vector3[] environmentPoints, Vector3 sensorPosition, Quaternion sensorRotation)
    {
        float[] ranges = new float[maxBeams];
        float[] intensities = new float[maxBeams];

        // Initialize all ranges to maximum
        for (int i = 0; i < maxBeams; i++)
        {
            ranges[i] = float.MaxValue;
        }

        // Process environment points
        foreach (Vector3 point in environmentPoints)
        {
            // Transform point to sensor frame
            Vector3 relativePoint = Quaternion.Inverse(sensorRotation) * (point - sensorPosition);

            // Calculate range and angle
            float range = relativePoint.magnitude;
            float angle = Mathf.Atan2(relativePoint.x, relativePoint.z);  // Azimuth angle

            // Find corresponding beam
            int beamIndex = Mathf.RoundToInt((angle + (fovHorizontal * Mathf.Deg2Rad / 2)) / (fovHorizontal * Mathf.Deg2Rad) * (maxBeams - 1));

            if (beamIndex >= 0 && beamIndex < maxBeams)
            {
                // Update range if closer than current reading
                if (range < ranges[beamIndex])
                {
                    ranges[beamIndex] = range;

                    // Calculate intensity based on reflectivity and distance
                    intensities[beamIndex] = CalculateReturnIntensity(range, point);
                }
            }
        }

        // Apply noise to all ranges
        for (int i = 0; i < maxBeams; i++)
        {
            if (ranges[i] < float.MaxValue)
            {
                ranges[i] = ApplyLiDARNoise(ranges[i], i, intensities[i]);
            }
            else
            {
                ranges[i] = 0f;  // No return
            }
        }

        return ranges;
    }

    float ApplyLiDARNoise(float trueRange, int beamIndex, float intensity)
    {
        float noisyRange = trueRange;

        // Environmental effects
        float envFactor = 1.0f;
        if (envEffects != null)
        {
            envFactor = envEffects.CalculateEnvironmentalNoiseFactor();
        }

        // Range-dependent noise
        float rangeNoise = baseRangeNoise * envFactor + (trueRange * rangeDependentNoise * envFactor);

        // Angular noise (affects range accuracy due to beam width)
        float angularNoiseEffect = Mathf.Tan(angularNoise) * trueRange;

        // Atmospheric attenuation effect
        float attenuationEffect = trueRange * atmosphericAttenuation;

        // Weather visibility effect
        float weatherEffect = (1.0f - weatherVisibility) * 0.1f;  // Additional error in poor visibility

        // Combine all noise sources
        float totalNoiseStdDev = Mathf.Sqrt(
            rangeNoise * rangeNoise +
            angularNoiseEffect * angularNoiseEffect +
            attenuationEffect * attenuationEffect +
            weatherEffect * weatherEffect
        );

        // Generate noise
        float noise = noiseModel.GenerateWhiteNoise() * totalNoiseStdDev;

        // Apply multipath interference
        float multipathNoise = 0f;
        if (Random.value < multipathFactor)
        {
            // Simulate ghost return
            multipathNoise = Random.Range(-0.1f, 0.1f);  // ±10cm ghost
        }

        noisyRange += noise + multipathNoise;

        // Ensure positive range
        noisyRange = Mathf.Max(0.05f, noisyRange);  // Minimum detectable range

        return noisyRange;
    }

    float CalculateReturnIntensity(float range, Vector3 hitPoint)
    {
        // Simplified intensity calculation based on:
        // - Distance (inverse square law)
        // - Surface normal (cosine law)
        // - Material reflectivity (simplified)

        // Base intensity decreases with distance
        float distanceFactor = 1.0f / (range * range + 0.01f);  // +0.01 to prevent division by zero

        // Surface normal effect (simplified)
        // In real implementation, this would use actual surface normals
        float normalFactor = 1.0f;

        // Material reflectivity (simplified)
        float reflectivity = 0.5f;  // Average reflectivity

        float baseIntensity = distanceFactor * normalFactor * reflectivity;

        // Add noise to intensity
        float intensityNoise = noiseModel.GenerateWhiteNoise() * intensityNoise;
        float noisyIntensity = Mathf.Clamp01(baseIntensity + intensityNoise);

        return noisyIntensity;
    }

    public void UpdateWeatherConditions(float visibility, float precipitation)
    {
        // Adjust parameters based on weather
        weatherVisibility = Mathf.Clamp01(visibility);

        // Increase noise in bad weather
        baseRangeNoise *= (1.0f + precipitation * 0.5f);
        atmosphericAttenuation *= (1.0f + precipitation * 0.2f);
    }

    void Update()
    {
        // Update weather effects if needed
        if (envEffects != null)
        {
            // Could update weather conditions dynamically
        }
    }
}
```

## Sensor Calibration Simulation

### Simulating Calibration Procedures

```csharp
using UnityEngine;
using System.Collections.Generic;

public class UnitySensorCalibrator : MonoBehaviour
{
    [Header("Calibration Parameters")]
    public bool enableAutoCalibration = true;
    public float calibrationInterval = 60.0f;  // Seconds
    public float calibrationAccuracy = 0.001f;  // Target accuracy

    [Header("Calibration Targets")]
    public GameObject[] calibrationTargets;
    public float calibrationDistance = 1.0f;
    public int calibrationIterations = 100;

    [Header("Calibration Results")]
    public bool calibrationSuccessful = false;
    public float calibrationError = float.MaxValue;
    public Vector3 positionBias;
    public Vector3 rotationBias;

    private float calibrationTimer = 0f;
    private List<SensorReading> calibrationData = new List<SensorReading>();

    [System.Serializable]
    public class SensorReading
    {
        public Vector3 measuredPosition;
        public Vector3 truePosition;
        public Vector3 measuredOrientation;
        public Vector3 trueOrientation;
        public float timestamp;
    }

    void Start()
    {
        if (enableAutoCalibration)
        {
            StartCoroutine(AutoCalibrationRoutine());
        }
    }

    IEnumerator AutoCalibrationRoutine()
    {
        while (true)
        {
            yield return new WaitForSeconds(calibrationInterval);
            PerformCalibration();
        }
    }

    public void PerformCalibration()
    {
        calibrationData.Clear();

        // Collect calibration data
        for (int i = 0; i < calibrationIterations; i++)
        {
            SensorReading reading = CollectCalibrationReading();
            calibrationData.Add(reading);

            yield return new WaitForSeconds(0.1f);  // Small delay between readings
        }

        // Calculate calibration parameters
        CalculateCalibrationParameters();
    }

    SensorReading CollectCalibrationReading()
    {
        // In real implementation, this would collect actual sensor data
        // For simulation, we'll create a reading with known errors

        SensorReading reading = new SensorReading();

        // Select a random calibration target
        GameObject target = calibrationTargets[Random.Range(0, calibrationTargets.Length)];

        // True values
        reading.truePosition = target.transform.position;
        reading.trueOrientation = target.transform.eulerAngles;

        // Simulate sensor reading with current biases
        reading.measuredPosition = reading.truePosition + positionBias + GetRandomNoiseVector(0.01f);
        reading.measuredOrientation = reading.trueOrientation + rotationBias + GetRandomNoiseVector(0.01f);

        reading.timestamp = Time.time;

        return reading;
    }

    void CalculateCalibrationParameters()
    {
        // Calculate position bias
        Vector3 positionSum = Vector3.zero;
        Vector3 orientationSum = Vector3.zero;

        foreach (SensorReading reading in calibrationData)
        {
            positionSum += (reading.measuredPosition - reading.truePosition);
            orientationSum += (reading.measuredOrientation - reading.trueOrientation);
        }

        Vector3 newPositionBias = positionSum / calibrationData.Count;
        Vector3 newRotationBias = orientationSum / calibrationData.Count;

        // Calculate error
        float totalError = 0f;
        foreach (SensorReading reading in calibrationData)
        {
            Vector3 correctedPosition = reading.measuredPosition - newPositionBias;
            Vector3 correctedOrientation = reading.measuredOrientation - newRotationBias;

            float positionError = Vector3.Distance(correctedPosition, reading.truePosition);
            float orientationError = Vector3.Distance(correctedOrientation, reading.trueOrientation);

            totalError += positionError + orientationError;
        }

        calibrationError = totalError / calibrationData.Count;

        // Update biases if calibration is sufficiently accurate
        if (calibrationError < calibrationAccuracy)
        {
            positionBias = newPositionBias;
            rotationBias = newRotationBias;
            calibrationSuccessful = true;

            Debug.Log($"Calibration successful! Error: {calibrationError:F4}m, Position bias: {positionBias}, Rotation bias: {rotationBias}");
        }
        else
        {
            calibrationSuccessful = false;
            Debug.LogWarning($"Calibration failed! Error: {calibrationError:F4}m (target: {calibrationAccuracy}m)");
        }
    }

    Vector3 GetRandomNoiseVector(float stdDev)
    {
        return new Vector3(
            GenerateGaussianNoise(stdDev),
            GenerateGaussianNoise(stdDev),
            GenerateGaussianNoise(stdDev)
        );
    }

    float GenerateGaussianNoise(float stdDev)
    {
        float u1 = Random.Range(0.0000001f, 1.0f);
        float u2 = Random.Range(0.0f, 1.0f);
        float gaussian = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Cos(2.0f * Mathf.PI * u2);
        return gaussian * stdDev;
    }

    public Vector3 ApplyPositionCorrection(Vector3 rawPosition)
    {
        return rawPosition - positionBias;
    }

    public Vector3 ApplyOrientationCorrection(Vector3 rawOrientation)
    {
        return rawOrientation - rotationBias;
    }

    public void ResetCalibration()
    {
        positionBias = Vector3.zero;
        rotationBias = Vector3.zero;
        calibrationSuccessful = false;
        calibrationError = float.MaxValue;
        calibrationData.Clear();
    }
}
```

## Validation of Noise Models

### Comparing Simulation to Real Data

```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class NoiseModelValidator : MonoBehaviour
{
    [Header("Validation Parameters")]
    public float noiseStdDevTolerance = 0.001f;
    public float biasTolerance = 0.001f;
    public float driftRateTolerance = 0.0001f;
    public int validationSamples = 1000;

    [Header("Real vs Simulated Data")]
    public float[] realNoiseData;
    public float[] simulatedNoiseData;

    private Dictionary<string, float[]> validationResults = new Dictionary<string, float[]>();

    public class ValidationMetrics
    {
        public float meanError;
        public float stdDevError;
        public float biasError;
        public float correlationError;
        public bool isValid;
    }

    public ValidationMetrics ValidateNoiseCharacteristics()
    {
        ValidationMetrics metrics = new ValidationMetrics();

        if (realNoiseData == null || simulatedNoiseData == null ||
            realNoiseData.Length != simulatedNoiseData.Length)
        {
            metrics.isValid = false;
            return metrics;
        }

        // Calculate statistical properties
        float realMean = realNoiseData.Average();
        float simMean = simulatedNoiseData.Average();

        float realStdDev = CalculateStandardDeviation(realNoiseData, realMean);
        float simStdDev = CalculateStandardDeviation(simulatedNoiseData, simMean);

        // Compare means (should be ~0 for zero-mean noise)
        metrics.meanError = Mathf.Abs(realMean - simMean);

        // Compare standard deviations
        metrics.stdDevError = Mathf.Abs(realStdDev - simStdDev);

        // Check if within tolerances
        metrics.isValid = metrics.meanError < noiseStdDevTolerance &&
                        metrics.stdDevError < noiseStdDevTolerance;

        return metrics;
    }

    public ValidationMetrics ValidateTemporalCharacteristics()
    {
        ValidationMetrics metrics = new ValidationMetrics();

        if (realNoiseData == null || simulatedNoiseData == null ||
            realNoiseData.Length != simulatedNoiseData.Length)
        {
            metrics.isValid = false;
            return metrics;
        }

        // Calculate autocorrelation to validate temporal characteristics
        float realAutocorr = CalculateAutocorrelation(realNoiseData, 1);  // Lag 1
        float simAutocorr = CalculateAutocorrelation(simulatedNoiseData, 1);

        metrics.correlationError = Mathf.Abs(realAutocorr - simAutocorr);
        metrics.isValid = metrics.correlationError < noiseStdDevTolerance;

        return metrics;
    }

    float CalculateStandardDeviation(float[] data, float mean)
    {
        float sum = 0f;
        foreach (float value in data)
        {
            sum += Mathf.Pow(value - mean, 2);
        }
        return Mathf.Sqrt(sum / data.Length);
    }

    float CalculateAutocorrelation(float[] data, int lag)
    {
        if (lag >= data.Length) return 0f;

        float mean = data.Average();
        float numerator = 0f;
        float denominator = 0f;

        // Calculate means-adjusted data
        float[] adjustedData = new float[data.Length];
        for (int i = 0; i < data.Length; i++)
        {
            adjustedData[i] = data[i] - mean;
        }

        // Calculate autocorrelation
        for (int i = 0; i < data.Length - lag; i++)
        {
            numerator += adjustedData[i] * adjustedData[i + lag];
        }

        for (int i = 0; i < data.Length; i++)
        {
            denominator += adjustedData[i] * adjustedData[i];
        }

        return denominator != 0 ? numerator / denominator : 0f;
    }

    public void GenerateNoiseReport()
    {
        ValidationMetrics noiseMetrics = ValidateNoiseCharacteristics();
        ValidationMetrics temporalMetrics = ValidateTemporalCharacteristics();

        Debug.Log($"Noise Validation Report:");
        Debug.Log($"  Mean Error: {noiseMetrics.meanError:F6} (tolerance: {noiseStdDevTolerance})");
        Debug.Log($"  Std Dev Error: {noiseMetrics.stdDevError:F6} (tolerance: {noiseStdDevTolerance})");
        Debug.Log($"  Autocorrelation Error: {temporalMetrics.correlationError:F6}");
        Debug.Log($"  Overall Valid: {noiseMetrics.isValid && temporalMetrics.isValid}");
    }

    public void CollectValidationData(System.Func<float[]> getRealData, System.Func<float[]> getSimData, int durationSeconds)
    {
        // Collect data over time for validation
        StartCoroutine(CollectValidationDataCoroutine(getRealData, getSimData, durationSeconds));
    }

    IEnumerator CollectValidationDataCoroutine(System.Func<float[]> getRealData, System.Func<float[]> getSimData, int duration)
    {
        List<float> realDataCollection = new List<float>();
        List<float> simDataCollection = new List<float>();

        float startTime = Time.time;
        while (Time.time - startTime < duration)
        {
            float[] realData = getRealData?.Invoke();
            float[] simData = getSimData?.Invoke();

            if (realData != null && simData != null)
            {
                realDataCollection.AddRange(realData);
                simDataCollection.AddRange(simData);
            }

            yield return new WaitForSeconds(0.1f);
        }

        realNoiseData = realDataCollection.ToArray();
        simulatedNoiseData = simDataCollection.ToArray();

        GenerateNoiseReport();
    }
}
```

## Integration with VLA Systems

Realistic noise modeling enables:
- **Robust Perception**: Systems that work despite sensor imperfections
- **Realistic Training**: Neural networks trained on realistic data distributions
- **Safety Validation**: Testing under worst-case sensor conditions
- **Performance Prediction**: Estimating real-world performance from simulation
- **Calibration Procedures**: Testing automatic calibration algorithms

## Best Practices

1. **Validate Against Real Data**: Always compare simulation noise to real sensor data
2. **Environmental Modeling**: Include realistic environmental effects
3. **Temporal Correlation**: Model time-correlated noise where appropriate
4. **Multi-sensor Fusion**: Test how noise affects sensor fusion algorithms
5. **Edge Case Testing**: Test under extreme noise conditions
6. **Calibration Integration**: Include calibration procedures in simulation
7. **Performance Monitoring**: Track how noise affects system performance
8. **Iterative Refinement**: Continuously improve noise models based on validation

This comprehensive noise modeling system provides the realistic sensor imperfections necessary for developing robust humanoid robot systems that can handle real-world sensor limitations.