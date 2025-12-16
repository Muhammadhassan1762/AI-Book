---
title: RGB, Depth, Segmentation Generation
sidebar_position: 3
---

# RGB, Depth, Segmentation Generation

This section covers the process of generating RGB, Depth, and Segmentation datasets using Isaac Sim's Replicator framework, including implementation details and quality validation.

## RGB Image Generation

RGB images form the foundation of most computer vision tasks in robotics. Isaac Sim's Replicator provides high-quality RGB image generation with realistic rendering.

### RGB Generation Pipeline

The RGB generation pipeline involves:
1. Scene rendering with realistic lighting
2. Camera capture with proper calibration
3. Image encoding and storage
4. Metadata annotation

### RGB Configuration Parameters

Key parameters for RGB generation:
- **Resolution**: Typically 640x480, 1280x720, or higher
- **Frame Rate**: Usually 30 FPS for video-like sequences
- **Format**: PNG for lossless, JPEG for size efficiency
- **Color Space**: sRGB with proper gamma correction

### Example RGB Generation Code

```python
import omni.replicator.core as rep

# Create RGB camera
rgb_camera = rep.create.camera()

# Attach RGB annotator
rgb_annotator = rep.AnnotatorRegistry.get_annotator("rgb")
rgb_annotator.attach([rgb_camera])

# Define capture sequence
with rep.trigger.on_frame(num_frames=1000):
    # Randomize lighting
    with rep.randomizer.on_alternate_lighting(light_budget=100):
        rep.randomizer.lighting(
            intensity_mean=rep.distribution.normal(3000, 1000),
            color_temperature=rep.distribution.uniform(5000, 8000)
        )

    # Randomize camera pose
    camera_poses = rep.distribution.uniform((-5, -5, 1), (5, 5, 5))
    rep.modify_pose(
        rgb_camera,
        position=camera_poses,
        rotation=rep.distribution.uniform((-1, -1, -1, -1), (1, 1, 1, 1))
    )

# Setup writer for RGB data
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="_isaac_sim_output/rgb_dataset",
    rgb=True,
    overwrite=True
)
writer.attach([rgb_annotator])
```

## Depth Image Generation

Depth images provide crucial 3D information for robotics tasks such as obstacle detection, mapping, and navigation.

### Depth Generation Pipeline

The depth generation process:
1. Scene depth calculation
2. Depth value encoding
3. Depth map generation
4. Validation and storage

### Depth Configuration Parameters

Important depth parameters:
- **Depth Range**: Near and far clipping planes (e.g., 0.1m to 100m)
- **Precision**: 16-bit or 32-bit floating point
- **Units**: Meters for consistency with robotics applications
- **Format**: PNG (16-bit) or EXR (32-bit float)

### Example Depth Generation Code

```python
import omni.replicator.core as rep

# Create depth camera (co-located with RGB if needed)
depth_camera = rep.create.camera()

# Attach depth annotator
depth_annotator = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
depth_annotator.attach([depth_camera])

# Define depth capture sequence
with rep.trigger.on_frame(num_frames=1000):
    # Randomize lighting
    with rep.randomizer.on_alternate_lighting(light_budget=100):
        rep.randomizer.lighting(
            intensity_mean=rep.distribution.normal(3000, 1000),
            color_temperature=rep.distribution.uniform(5000, 8000)
        )

    # Randomize camera poses
    camera_poses = rep.distribution.uniform((-5, -5, 1), (5, 5, 5))
    rep.modify_pose(
        depth_camera,
        position=camera_poses,
        rotation=rep.distribution.uniform((-1, -1, -1, -1), (1, 1, 1, 1))
    )

# Setup writer for depth data
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="_isaac_sim_output/depth_dataset",
    distance_to_camera=True,
    overwrite=True
)
writer.attach([depth_annotator])
```

## Segmentation Generation

Segmentation provides pixel-level object classification, essential for scene understanding in robotics.

### Segmentation Types

Two main types of segmentation:
- **Semantic Segmentation**: Each pixel labeled with object class
- **Instance Segmentation**: Each pixel labeled with object instance ID

### Segmentation Pipeline

The segmentation process includes:
1. Object labeling in the scene
2. Pixel-wise classification
3. Mask generation
4. Annotation creation

### Example Segmentation Generation Code

```python
import omni.replicator.core as rep

# Create segmentation camera
seg_camera = rep.create.camera()

# Attach segmentation annotator (instance segmentation)
seg_annotator = rep.AnnotatorRegistry.get_annotator("instance_segmentation")
seg_annotator.attach([seg_camera])

# Define segmentation capture sequence
with rep.trigger.on_frame(num_frames=1000):
    # Randomize lighting
    with rep.randomizer.on_alternate_lighting(light_budget=100):
        rep.randomizer.lighting(
            intensity_mean=rep.distribution.normal(3000, 1000),
            color_temperature=rep.distribution.uniform(5000, 8000)
        )

    # Randomize camera poses
    camera_poses = rep.distribution.uniform((-5, -5, 1), (5, 5, 5))
    rep.modify_pose(
        seg_camera,
        position=camera_poses,
        rotation=rep.distribution.uniform((-1, -1, -1, -1), (1, 1, 1, 1))
    )

# Setup writer for segmentation data
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="_isaac_sim_output/segmentation_dataset",
    instance_segmentation=True,
    overwrite=True
)
writer.attach([seg_annotator])
```

## Multi-Modal Dataset Generation

For robotics applications, it's often necessary to generate all three modalities simultaneously with perfect alignment.

### Synchronized Capture

To ensure perfect alignment between modalities:
- Use the same camera pose for all modalities
- Capture simultaneously in the same frame
- Maintain consistent timestamps
- Validate geometric alignment

### Example Multi-Modal Generation

```python
import omni.replicator.core as rep

# Create a single camera for all modalities
main_camera = rep.create.camera()

# Attach multiple annotators
rgb_annotator = rep.AnnotatorRegistry.get_annotator("rgb")
depth_annotator = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
seg_annotator = rep.AnnotatorRegistry.get_annotator("instance_segmentation")

rgb_annotator.attach([main_camera])
depth_annotator.attach([main_camera])
seg_annotator.attach([main_camera])

# Define capture sequence for all modalities
with rep.trigger.on_frame(num_frames=1000):
    # Randomize lighting
    with rep.randomizer.on_alternate_lighting(light_budget=100):
        rep.randomizer.lighting(
            intensity_mean=rep.distribution.normal(3000, 1000),
            color_temperature=rep.distribution.uniform(5000, 8000)
        )

    # Randomize camera poses
    camera_poses = rep.distribution.uniform((-5, -5, 1), (5, 5, 5))
    rep.modify_pose(
        main_camera,
        position=camera_poses,
        rotation=rep.distribution.uniform((-1, -1, -1, -1), (1, 1, 1, 1))
    )

# Setup writer for multi-modal data
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="_isaac_sim_output/multi_modal_dataset",
    rgb=True,
    distance_to_camera=True,
    instance_segmentation=True,
    overwrite=True
)
writer.attach([rgb_annotator, depth_annotator, seg_annotator])
```

## Quality Validation

### RGB Quality Checks
- Color accuracy and consistency
- Resolution and aspect ratio
- Exposure and contrast
- Absence of rendering artifacts

### Depth Quality Checks
- Depth range validity
- Precision and accuracy
- Absence of holes or invalid values
- Alignment with RGB images

### Segmentation Quality Checks
- Label accuracy
- Boundary precision
- Instance separation
- Consistency across frames

## Performance Optimization

### Scene Complexity Management
- Use level of detail (LOD) for complex objects
- Optimize polygon counts
- Use efficient materials and textures
- Batch process multiple scenes

### Memory Management
- Process data in manageable chunks
- Use efficient image formats
- Monitor GPU memory usage
- Implement streaming where possible

## Dataset Formats

### Output Structure
A typical dataset follows this structure:
```
dataset/
├── rgb/
│   ├── image_000001.png
│   ├── image_000002.png
│   └── ...
├── depth/
│   ├── depth_000001.png
│   ├── depth_000002.png
│   └── ...
├── segmentation/
│   ├── seg_000001.png
│   ├── seg_000002.png
│   └── ...
└── annotations.json
```

### Annotation Format
Annotations typically include:
- Camera intrinsics and extrinsics
- Object bounding boxes (if applicable)
- Class labels and instance IDs
- Timestamps and metadata

## Best Practices for Robotics Applications

### Realism Considerations
- Match real-world lighting conditions
- Include sensor noise and artifacts
- Use appropriate depth ranges
- Ensure realistic object interactions

### Diversity Strategies
- Vary lighting conditions (indoor/outdoor, day/night)
- Change weather conditions (clear, foggy, rainy)
- Adjust camera positions and angles
- Modify object configurations and layouts

This completes the generation of RGB, Depth, and Segmentation datasets using Isaac Sim. The next section will cover validation and testing of these datasets.