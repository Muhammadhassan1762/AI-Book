---
sidebar_position: 2
---

# High-Fidelity Rendering

## Creating Photorealistic Environments for Humanoid Robot Perception

High-fidelity rendering in Unity creates photorealistic environments that are essential for training and validating perception systems in humanoid robots. This level of visual realism enables synthetic data generation that can bridge the gap between simulation and reality for vision-based systems.

## Learning Objectives

By the end of this chapter, you will:
- Master Unity's rendering pipeline for robotics applications
- Configure advanced lighting and materials for realistic perception
- Generate synthetic data with photorealistic quality
- Optimize rendering performance for real-time simulation
- Validate rendering fidelity for perception system training

## Unity Rendering Pipeline for Robotics

### Universal Render Pipeline (URP) Configuration

For robotics applications, URP provides the right balance of quality and performance:

```csharp
// URP Asset Configuration (Scriptable Object)
using UnityEngine;
using UnityEngine.Rendering.Universal;

[CreateAssetMenu(fileName = "RoboticsURPAsset", menuName = "Rendering/Robotics URP Asset")]
public class RoboticsURPAsset : UniversalRenderPipelineAsset
{
    [Header("Lighting Settings")]
    public bool supportsMainLightShadows = true;
    public bool supportsAdditionalLights = true;
    public int maxAdditionalLightsCount = 8;

    [Header("Shadow Settings")]
    public float shadowDistance = 50.0f;
    public int shadowCascadeCount = 4;
    public float cascade2Split = 0.25f;
    public float cascade3Split = 0.1f;
    public float cascade4Split = 0.067f;

    [Header("Post-Processing")]
    public bool supportsPostProcessing = true;
    public bool supportsDepthTexture = true;
    public bool supportsColorGrading = false; // Disable for synthetic data consistency

    protected override void OnValidate()
    {
        base.OnValidate();

        // Configure URP settings for robotics
        supportsMainLightShadows = true;
        supportsAdditionalLights = supportsAdditionalLights;
        maxAdditionalLightsCount = Mathf.Clamp(maxAdditionalLightsCount, 0, 16);

        shadowDistance = Mathf.Clamp(shadowDistance, 5.0f, 100.0f);
        shadowCascadeCount = Mathf.Clamp(shadowCascadeCount, 1, 4);
    }
}
```

### Custom Rendering Pipeline for Synthetic Data

```csharp
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public class SyntheticDataRenderer : ScriptableRendererFeature
{
    class SyntheticDataRenderPass : ScriptableRenderPass
    {
        private RenderTargetIdentifier source;
        private RenderTargetHandle temporaryColorTexture;
        private Material postProcessMaterial;

        public SyntheticDataRenderPass(Material material)
        {
            this.postProcessMaterial = material;
            this.renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing;
        }

        public override void Configure(CommandBuffer cmd, RenderTextureDescriptor cameraTextureDescriptor)
        {
            // Configure render texture for synthetic data
            cameraTextureDescriptor.colorFormat = RenderTextureFormat.ARGB32;
            cameraTextureDescriptor.depthBufferBits = 24;

            temporaryColorTexture.Init("_TemporaryColorTexture");
            cmd.GetTemporaryRT(temporaryColorTexture.id, cameraTextureDescriptor, FilterMode.Point);
        }

        public override void Execute(ScriptableRenderContext context, ref RenderingData renderingData)
        {
            if (postProcessMaterial == null) return;

            CommandBuffer cmd = CommandBufferPool.Get("SyntheticDataRenderPass");

            // Blit source to temporary texture
            source = renderingData.cameraData.renderer.cameraColorTarget;
            cmd.Blit(source, temporaryColorTexture.Identifier(), postProcessMaterial, 0);

            // Blit back to camera
            cmd.Blit(temporaryColorTexture.Identifier(), source);

            context.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
        }

        public override void FrameCleanup(CommandBuffer cmd)
        {
            if (temporaryColorTexture != RenderTargetHandle.CameraTarget)
            {
                cmd.ReleaseTemporaryRT(temporaryColorTexture.id);
            }
        }
    }

    public Material postProcessMaterial;

    public override void Create()
    {
        var pass = new SyntheticDataRenderPass(postProcessMaterial);
        pass.renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing;
        this.scriptablePass = pass;
    }

    private SyntheticDataRenderPass scriptablePass;

    public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
    {
        renderer.EnqueuePass(scriptablePass);
    }
}
```

## Advanced Lighting for Photorealism

### Realistic Lighting Setup

```csharp
using UnityEngine;

public class AdvancedLightingSetup : MonoBehaviour
{
    [Header("Lighting Configuration")]
    public Light mainDirectionalLight;
    public Light[] areaLights;
    public ReflectionProbe reflectionProbe;

    [Header("Environment Lighting")]
    public Gradient skyGradient;
    public float ambientIntensity = 1.0f;

    void Start()
    {
        SetupMainLighting();
        SetupAreaLights();
        ConfigureReflectionProbes();
        SetupSkybox();
    }

    void SetupMainLighting()
    {
        // Configure main directional light with realistic properties
        mainDirectionalLight.type = LightType.Directional;
        mainDirectionalLight.color = Color.white;
        mainDirectionalLight.intensity = 3.14f; // Physically accurate (π for direct sunlight)
        mainDirectionalLight.shadows = LightShadows.Soft;
        mainDirectionalLight.shadowStrength = 1.0f;
        mainDirectionalLight.shadowResolution = UnityEngine.Rendering.LightShadowResolution.High;
        mainDirectionalLight.shadowBias = 0.05f;
        mainDirectionalLight.shadowNormalBias = 0.4f;
        mainDirectionalLight.shadowNearPlane = 0.2f;

        // Set realistic sun direction
        mainDirectionalLight.transform.rotation = Quaternion.Euler(45f, 30f, 0f);
    }

    void SetupAreaLights()
    {
        foreach (Light areaLight in areaLights)
        {
            // Configure area lights for soft, realistic lighting
            areaLight.type = LightType.Rectangle;
            areaLight.intensity = 2.0f;
            areaLight.color = Color.white;
            areaLight.shadows = LightShadows.Soft;
            areaLight.shadowResolution = UnityEngine.Rendering.LightShadowResolution.Medium;

            // Set area light properties (Unity Pro feature)
            // areaLight.areaSize = new Vector2(2f, 2f);
        }
    }

    void ConfigureReflectionProbes()
    {
        // Configure reflection probe for realistic reflections
        reflectionProbe.mode = UnityEngine.Rendering.ReflectionProbeMode.Realtime;
        reflectionProbe.refreshMode = UnityEngine.Rendering.ReflectionProbeRefreshMode.ViaScriptingUpdates;
        reflectionProbe.timeSlicingMode = UnityEngine.Rendering.ReflectionProbeTimeSlicingMode.IndividualFaces;
        reflectionProbe.resolution = 512; // Balance quality with performance
        reflectionProbe.intensity = 1.0f;
        reflectionProbe.shadowDistance = 100f;
    }

    void SetupSkybox()
    {
        // Create and configure realistic skybox
        var skyboxMaterial = new Material(Shader.Find("Skybox/Procedural"));
        skyboxMaterial.SetFloat("_SunSize", 0.04f);
        skyboxMaterial.SetFloat("_AtmosphereThickness", 1.0f);
        skyboxMaterial.SetColor("_SkyTint", Color.blue);
        skyboxMaterial.SetColor("_GroundColor", Color.gray);

        RenderSettings.skybox = skyboxMaterial;
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
        RenderSettings.ambientIntensity = ambientIntensity;
        RenderSettings.ambientSkyColor = skyGradient.Evaluate(1.0f);
        RenderSettings.ambientEquatorColor = skyGradient.Evaluate(0.5f);
        RenderSettings.ambientGroundColor = skyGradient.Evaluate(0.0f);
    }

    void Update()
    {
        // Add dynamic lighting variations for realism
        float timeVariation = Mathf.Sin(Time.time * 0.05f) * 0.1f;
        mainDirectionalLight.intensity = 3.14f + timeVariation;
    }
}
```

## Material System for Realistic Surfaces

### Physically-Based Materials

```csharp
using UnityEngine;

public class RealisticMaterialSetup : MonoBehaviour
{
    [Header("Material Properties")]
    public Material[] robotMaterials;
    public Material[] environmentMaterials;
    public Material[] humanSkinMaterials;

    void Start()
    {
        ConfigureRobotMaterials();
        ConfigureEnvironmentMaterials();
        ConfigureHumanSkinMaterials();
    }

    void ConfigureRobotMaterials()
    {
        foreach (Material material in robotMaterials)
        {
            // Configure metallic surfaces
            if (material.name.Contains("metal") || material.name.Contains("Metal"))
            {
                ConfigureMetallicMaterial(material);
            }
            // Configure plastic surfaces
            else if (material.name.Contains("plastic") || material.name.Contains("Plastic"))
            {
                ConfigurePlasticMaterial(material);
            }
            // Configure rubber surfaces
            else if (material.name.Contains("rubber") || material.name.Contains("Rubber"))
            {
                ConfigureRubberMaterial(material);
            }
        }
    }

    void ConfigureMetallicMaterial(Material material)
    {
        material.SetFloat("_Metallic", 0.9f); // High metallic
        material.SetFloat("_Smoothness", 0.8f); // High smoothness
        material.SetColor("_BaseColor", new Color(0.7f, 0.7f, 0.8f, 1.0f)); // Silver-like
        material.EnableKeyword("_NORMALMAP");
        material.EnableKeyword("_METALLICSPECGLOSSMAP");
    }

    void ConfigurePlasticMaterial(Material material)
    {
        material.SetFloat("_Metallic", 0.0f); // Non-metallic
        material.SetFloat("_Smoothness", 0.4f); // Moderate smoothness
        material.SetColor("_BaseColor", new Color(0.8f, 0.8f, 0.9f, 1.0f)); // Plastic-like
        material.EnableKeyword("_NORMALMAP");
    }

    void ConfigureRubberMaterial(Material material)
    {
        material.SetFloat("_Metallic", 0.0f); // Non-metallic
        material.SetFloat("_Smoothness", 0.2f); // Matte finish
        material.SetColor("_BaseColor", new Color(0.1f, 0.1f, 0.1f, 1.0f)); // Black rubber
        material.EnableKeyword("_NORMALMAP");
    }

    void ConfigureEnvironmentMaterials()
    {
        foreach (Material material in environmentMaterials)
        {
            if (material.name.Contains("wood") || material.name.Contains("Wood"))
            {
                ConfigureWoodMaterial(material);
            }
            else if (material.name.Contains("floor") || material.name.Contains("Floor"))
            {
                ConfigureFloorMaterial(material);
            }
            else if (material.name.Contains("wall") || material.name.Contains("Wall"))
            {
                ConfigureWallMaterial(material);
            }
        }
    }

    void ConfigureWoodMaterial(Material material)
    {
        material.SetFloat("_Metallic", 0.0f);
        material.SetFloat("_Smoothness", 0.3f);
        material.SetColor("_BaseColor", new Color(0.6f, 0.4f, 0.2f, 1.0f)); // Wood color
        material.EnableKeyword("_NORMALMAP");
        material.EnableKeyword("_OCCLUSIONMAP");
    }

    void ConfigureFloorMaterial(Material material)
    {
        material.SetFloat("_Metallic", 0.0f);
        material.SetFloat("_Smoothness", 0.1f); // Matte for floors
        material.SetColor("_BaseColor", new Color(0.5f, 0.5f, 0.5f, 1.0f)); // Neutral floor
        material.EnableKeyword("_NORMALMAP");
    }

    void ConfigureWallMaterial(Material material)
    {
        material.SetFloat("_Metallic", 0.0f);
        material.SetFloat("_Smoothness", 0.05f); // Very matte
        material.SetColor("_BaseColor", new Color(0.9f, 0.9f, 0.9f, 1.0f)); // White wall
        material.EnableKeyword("_NORMALMAP");
    }

    void ConfigureHumanSkinMaterials()
    {
        foreach (Material material in humanSkinMaterials)
        {
            ConfigureSkinMaterial(material);
        }
    }

    void ConfigureSkinMaterial(Material material)
    {
        // Configure subsurface scattering for realistic skin
        material.SetFloat("_Metallic", 0.0f);
        material.SetFloat("_Smoothness", 0.2f); // Subtle gloss
        material.SetColor("_BaseColor", new Color(0.8f, 0.6f, 0.4f, 1.0f)); // Skin tone

        // Enable skin-specific features
        material.EnableKeyword("_SUBSURFACE_SCATTERING");
        material.EnableKeyword("_NORMALMAP");
        material.EnableKeyword("_OCCLUSIONMAP");
    }
}
```

## High-Quality Textures and UV Mapping

### Texture Streaming for Large Environments

```csharp
using UnityEngine;

public class TextureStreamingOptimizer : MonoBehaviour
{
    [Header("Texture Streaming Settings")]
    public float streamingMultiplier = 1.0f;
    public int maxTextureResolution = 2048;
    public float loadingRadius = 20.0f;

    void Start()
    {
        ConfigureTextureStreaming();
    }

    void ConfigureTextureStreaming()
    {
        // Configure texture streaming for large environments
        QualitySettings.streamingMipmapsActive = true;
        QualitySettings.streamingMipmapsAddAllCameras = true;
        QualitySettings.streamingMipmapsMemoryBudget = 512.0f; // MB
        QualitySettings.streamingMipmapsRenderersPerFrame = 512;
        QualitySettings.streamingMipmapsMaxLevelReduction = 2;
        QualitySettings.streamingMipmapsMaxFileIORequests = 1024;
    }

    void Update()
    {
        // Adjust streaming based on camera position
        AdjustStreamingForCamera();
    }

    void AdjustStreamingForCamera()
    {
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            // Set loading radius based on camera distance
            foreach (Renderer renderer in FindObjectsOfType<Renderer>())
            {
                float distance = Vector3.Distance(mainCamera.transform.position, renderer.transform.position);

                if (distance < loadingRadius)
                {
                    // Load higher resolution textures
                    renderer.enabled = true;
                }
                else
                {
                    // Use lower resolution textures or cull
                    renderer.enabled = distance < loadingRadius * 2;
                }
            }
        }
    }
}
```

## Synthetic Data Generation Pipeline

### Photorealistic Image Capture

```csharp
using UnityEngine;
using System.Collections;
using System.IO;
using System.Collections.Generic;

public class PhotorealisticDataCapture : MonoBehaviour
{
    [Header("Capture Configuration")]
    public Camera captureCamera;
    public int captureWidth = 1280;
    public int captureHeight = 720;
    public int captureRate = 30; // FPS
    public string outputPath = "SyntheticData/";

    [Header("Data Types")]
    public bool captureRGB = true;
    public bool captureDepth = true;
    public bool captureSemantic = true;
    public bool captureInstance = true;

    private RenderTexture rgbTexture;
    private RenderTexture depthTexture;
    private RenderTexture semanticTexture;
    private RenderTexture instanceTexture;

    private int sequenceCounter = 0;
    private int frameCounter = 0;

    void Start()
    {
        InitializeTextures();
        Directory.CreateDirectory(Path.Combine(Application.persistentDataPath, outputPath));
    }

    void InitializeTextures()
    {
        // RGB texture
        rgbTexture = new RenderTexture(captureWidth, captureHeight, 24, RenderTextureFormat.ARGB32);
        rgbTexture.Create();

        // Depth texture
        depthTexture = new RenderTexture(captureWidth, captureHeight, 24, RenderTextureFormat.Depth);
        depthTexture.Create();

        // Semantic segmentation texture (using different render texture)
        semanticTexture = new RenderTexture(captureWidth, captureHeight, 0, RenderTextureFormat.ARGB32);
        semanticTexture.Create();

        // Instance segmentation texture
        instanceTexture = new RenderTexture(captureWidth, captureHeight, 0, RenderTextureFormat.ARGB32);
        instanceTexture.Create();

        // Set camera render textures
        captureCamera.targetTexture = rgbTexture;
    }

    void Update()
    {
        if (frameCounter % (60 / captureRate) == 0) // Unity runs at 60 FPS
        {
            CaptureFrame();
        }
        frameCounter = (frameCounter + 1) % 60;
    }

    void CaptureFrame()
    {
        // Capture RGB image
        if (captureRGB)
        {
            CaptureRGBImage();
        }

        // Capture depth image
        if (captureDepth)
        {
            CaptureDepthImage();
        }

        // Capture semantic segmentation
        if (captureSemantic)
        {
            CaptureSemanticImage();
        }

        // Capture instance segmentation
        if (captureInstance)
        {
            CaptureInstanceImage();
        }

        sequenceCounter++;
    }

    void CaptureRGBImage()
    {
        RenderTexture.active = rgbTexture;
        Texture2D rgbTexture2D = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);
        rgbTexture2D.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
        rgbTexture2D.Apply();

        string rgbPath = Path.Combine(Application.persistentDataPath,
                                    outputPath,
                                    $"rgb_{sequenceCounter:D6}.png");
        File.WriteAllBytes(rgbPath, rgbTexture2D.EncodeToPNG());
        DestroyImmediate(rgbTexture2D);
    }

    void CaptureDepthImage()
    {
        // Render depth to texture using a custom depth shader
        // Implementation depends on your depth rendering setup
        RenderTexture.active = depthTexture;
        Texture2D depthTexture2D = new Texture2D(captureWidth, captureHeight, TextureFormat.RFloat, false);
        depthTexture2D.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
        depthTexture2D.Apply();

        string depthPath = Path.Combine(Application.persistentDataPath,
                                      outputPath,
                                      $"depth_{sequenceCounter:D6}.exr");
        File.WriteAllBytes(depthPath, depthTexture2D.EncodeToEXR());
        DestroyImmediate(depthTexture2D);
    }

    void CaptureSemanticImage()
    {
        // Render semantic segmentation using material IDs
        // This requires a custom semantic rendering pass
        RenderTexture.active = semanticTexture;
        Texture2D semanticTexture2D = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);
        semanticTexture2D.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
        semanticTexture2D.Apply();

        string semanticPath = Path.Combine(Application.persistentDataPath,
                                         outputPath,
                                         $"semantic_{sequenceCounter:D6}.png");
        File.WriteAllBytes(semanticPath, semanticTexture2D.EncodeToPNG());
        DestroyImmediate(semanticTexture2D);
    }

    void CaptureInstanceImage()
    {
        // Render instance segmentation using unique IDs per instance
        RenderTexture.active = instanceTexture;
        Texture2D instanceTexture2D = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);
        instanceTexture2D.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
        instanceTexture2D.Apply();

        string instancePath = Path.Combine(Application.persistentDataPath,
                                         outputPath,
                                         $"instance_{sequenceCounter:D6}.png");
        File.WriteAllBytes(instancePath, instanceTexture2D.EncodeToPNG());
        DestroyImmediate(instanceTexture2D);
    }

    void OnDestroy()
    {
        // Clean up render textures
        if (rgbTexture) rgbTexture.Release();
        if (depthTexture) depthTexture.Release();
        if (semanticTexture) semanticTexture.Release();
        if (instanceTexture) instanceTexture.Release();
    }
}
```

## Performance Optimization

### Rendering Quality vs Performance Balance

```csharp
using UnityEngine;

public class RenderingOptimizer : MonoBehaviour
{
    [Header("Performance Settings")]
    public int targetQualityLevel = 2; // 0=Low, 1=Medium, 2=High, 3=Ultra
    public float targetFrameRate = 30.0f;
    public bool enableDynamicLOD = true;

    [Header("LOD Configuration")]
    public float lodBias = 1.0f;
    public int maximumLODLevel = 0;

    void Start()
    {
        ApplyQualitySettings();
    }

    void ApplyQualitySettings()
    {
        // Set quality level based on target
        QualitySettings.SetQualityLevel(targetQualityLevel, true);

        // Configure LOD bias
        QualitySettings.lodBias = lodBias;
        QualitySettings.maximumLODLevel = maximumLODLevel;

        // Set target frame rate
        Application.targetFrameRate = Mathf.RoundToInt(targetFrameRate);

        // Configure shadow settings based on quality level
        ConfigureShadows();

        // Configure texture settings
        ConfigureTextures();

        // Configure particle settings
        ConfigureParticles();
    }

    void ConfigureShadows()
    {
        switch (targetQualityLevel)
        {
            case 0: // Low
                QualitySettings.shadowResolution = ShadowResolution.Low;
                QualitySettings.shadowDistance = 15.0f;
                QualitySettings.shadowCascades = 1;
                break;
            case 1: // Medium
                QualitySettings.shadowResolution = ShadowResolution.Medium;
                QualitySettings.shadowDistance = 30.0f;
                QualitySettings.shadowCascades = 2;
                break;
            case 2: // High
                QualitySettings.shadowResolution = ShadowResolution.High;
                QualitySettings.shadowDistance = 50.0f;
                QualitySettings.shadowCascades = 2;
                break;
            case 3: // Ultra
                QualitySettings.shadowResolution = ShadowResolution.VeryHigh;
                QualitySettings.shadowDistance = 100.0f;
                QualitySettings.shadowCascades = 4;
                break;
        }
    }

    void ConfigureTextures()
    {
        switch (targetQualityLevel)
        {
            case 0: // Low
                QualitySettings.masterTextureLimit = 2; // 1/4 resolution
                QualitySettings.anisotropicFiltering = AnisotropicFiltering.Disable;
                break;
            case 1: // Medium
                QualitySettings.masterTextureLimit = 1; // 1/2 resolution
                QualitySettings.anisotropicFiltering = AnisotropicFiltering.Enable;
                break;
            case 2: // High
                QualitySettings.masterTextureLimit = 0; // Full resolution
                QualitySettings.anisotropicFiltering = AnisotropicFiltering.Enable;
                break;
            case 3: // Ultra
                QualitySettings.masterTextureLimit = 0; // Full resolution
                QualitySettings.anisotropicFiltering = AnisotropicFiltering.ForceEnable;
                break;
        }
    }

    void ConfigureParticles()
    {
        switch (targetQualityLevel)
        {
            case 0: // Low
                QualitySettings.particleRaycastBudget = 4;
                break;
            case 1: // Medium
                QualitySettings.particleRaycastBudget = 16;
                break;
            case 2: // High
                QualitySettings.particleRaycastBudget = 64;
                break;
            case 3: // Ultra
                QualitySettings.particleRaycastBudget = 256;
                break;
        }
    }

    void Update()
    {
        if (enableDynamicLOD)
        {
            AdjustLODBasedOnPerformance();
        }
    }

    void AdjustLODBasedOnPerformance()
    {
        float currentFrameTime = Time.deltaTime;
        float targetFrameTime = 1.0f / targetFrameRate;

        if (currentFrameTime > targetFrameTime * 1.2f) // 20% over target
        {
            // Reduce quality to maintain performance
            if (lodBias > 0.5f)
            {
                lodBias -= 0.1f;
                QualitySettings.lodBias = Mathf.Max(0.5f, lodBias);
            }
        }
        else if (currentFrameTime < targetFrameTime * 0.8f) // 20% under target
        {
            // Increase quality if we have headroom
            if (lodBias < 2.0f)
            {
                lodBias += 0.1f;
                QualitySettings.lodBias = Mathf.Min(2.0f, lodBias);
            }
        }
    }
}
```

## Validation of Rendering Quality

### Perceptual Quality Assessment

```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class RenderingQualityValidator : MonoBehaviour
{
    [Header("Validation Settings")]
    public Camera referenceCamera;
    public Camera testCamera;
    public int validationResolution = 256;
    public float validationThreshold = 0.95f;

    private Texture2D referenceImage;
    private Texture2D testImage;

    public void ValidateRenderingQuality()
    {
        StartCoroutine(CompareRenderingQuality());
    }

    IEnumerator CompareRenderingQuality()
    {
        // Capture reference image (high quality)
        yield return new WaitForEndOfFrame();
        referenceImage = CaptureCameraImage(referenceCamera, validationResolution, validationResolution);

        // Capture test image (current settings)
        yield return new WaitForEndOfFrame();
        testImage = CaptureCameraImage(testCamera, validationResolution, validationResolution);

        // Compare images
        float similarity = CalculateImageSimilarity(referenceImage, testImage);

        Debug.Log($"Rendering quality: {similarity:F3} (threshold: {validationThreshold})");

        if (similarity < validationThreshold)
        {
            Debug.LogWarning("Rendering quality below threshold - consider adjusting settings");
        }
        else
        {
            Debug.Log("Rendering quality meets requirements");
        }

        // Cleanup
        DestroyImmediate(referenceImage);
        DestroyImmediate(testImage);
    }

    Texture2D CaptureCameraImage(Camera camera, int width, int height)
    {
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture renderTexture = RenderTexture.GetTemporary(width, height, 24);

        camera.targetTexture = renderTexture;
        camera.Render();

        RenderTexture.active = renderTexture;
        Texture2D image = new Texture2D(width, height, TextureFormat.RGB24, false);
        image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        image.Apply();

        // Restore
        camera.targetTexture = null;
        RenderTexture.active = currentRT;
        RenderTexture.ReleaseTemporary(renderTexture);

        return image;
    }

    float CalculateImageSimilarity(Texture2D img1, Texture2D img2)
    {
        // Simple pixel-by-pixel comparison (SSIM would be more sophisticated)
        Color[] pixels1 = img1.GetPixels();
        Color[] pixels2 = img2.GetPixels();

        if (pixels1.Length != pixels2.Length)
            return 0.0f;

        float similarity = 0.0f;
        for (int i = 0; i < pixels1.Length; i++)
        {
            float diff = Vector3.Distance(
                new Vector3(pixels1[i].r, pixels1[i].g, pixels1[i].b),
                new Vector3(pixels2[i].r, pixels2[i].g, pixels2[i].b)
            );
            similarity += (1.0f - diff);
        }

        return similarity / pixels1.Length;
    }
}
```

## Integration with VLA Systems

High-fidelity rendering enables:
- **Synthetic training data**: Photorealistic images for vision system training
- **Perception validation**: Testing vision algorithms in realistic conditions
- **Visual feedback**: Realistic rendering for human-robot interaction
- **Safety validation**: Visual hazard detection and avoidance testing
- **Scenario testing**: Diverse visual environments for VLA system validation

## Best Practices

1. **Use physically-based rendering**: Ensure materials and lighting are physically accurate
2. **Validate synthetic data quality**: Compare to real sensor data for consistency
3. **Optimize for performance**: Balance quality with real-time simulation requirements
4. **Document rendering parameters**: Record settings for reproducible results
5. **Test perception systems**: Validate that vision algorithms work with synthetic data
6. **Use appropriate textures**: High-quality but optimized for performance

This high-fidelity rendering system provides the photorealistic visual simulation necessary for developing and validating perception-based humanoid robot systems.