---
sidebar_position: 1
---

# Chapter 1: Synthetic Data Generation with Isaac Sim

## Creating Training Data for Vision Systems

Synthetic data generation is a revolutionary approach to creating training data for computer vision systems without requiring real-world data collection. Isaac Sim enables the creation of massive, diverse, and perfectly annotated datasets for training perception systems in humanoid robots.

## Learning Objectives

By the end of this chapter, you will:
- Understand the importance of synthetic data for perception training
- Configure Isaac Sim for synthetic data generation
- Create diverse training datasets with photorealistic quality
- Generate annotations for various computer vision tasks
- Validate synthetic data quality for real-world transfer
- Integrate synthetic data into machine learning workflows

## Why Synthetic Data?

Traditional data collection faces several challenges:
- **Cost**: Expensive and time-consuming to collect real data
- **Safety**: Dangerous scenarios difficult to collect safely
- **Diversity**: Hard to capture all possible scenarios
- **Annotations**: Manual annotation is labor-intensive
- **Privacy**: Real-world data may contain privacy concerns

Synthetic data addresses these challenges:
- **Cost-effective**: Generate unlimited data without physical collection
- **Safe**: Simulate dangerous scenarios without risk
- **Diverse**: Create varied scenarios and edge cases
- **Perfect Annotations**: Automatic generation of ground truth
- **Controllable**: Systematically vary parameters for robust training

## Isaac Sim for Data Generation

Isaac Sim provides several capabilities for synthetic data generation:

### Photorealistic Rendering
- **Physically-based rendering**: Accurate lighting and materials
- **High-fidelity textures**: Realistic surface appearances
- **Lighting simulation**: Dynamic lighting conditions
- **Camera simulation**: Accurate sensor modeling

### Scene Generation
- **Procedural environments**: Automatically generate diverse scenes
- **Object placement**: Systematic object arrangement
- **Environmental variation**: Different lighting, weather, and conditions
- **Randomization**: Domain randomization for robust training

### Annotation Generation
- **Semantic segmentation**: Pixel-perfect class labels
- **Instance segmentation**: Individual object masks
- **Bounding boxes**: 2D and 3D bounding box annotations
- **Keypoint detection**: 3D joint positions and orientations
- **Depth maps**: Accurate depth information
- **Surface normals**: Geometric information

## Setting Up Isaac Sim for Data Generation

### Basic Configuration

```python
# Python script for Isaac Sim data generation
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.synthetic_utils import SyntheticDataHelper
from pxr import UsdGeom, Gf
import numpy as np
import cv2
import os

class IsaacSimDataGenerator:
    def __init__(self, output_dir="synthetic_data", num_samples=1000):
        self.output_dir = output_dir
        self.num_samples = num_samples

        # Create output directories
        self.setup_directories()

        # Initialize Isaac Sim world
        self.world = World(stage_units_in_meters=1.0)

        # Setup synthetic data helper
        self.sd_helper = SyntheticDataHelper()

        # Data collection parameters
        self.camera_poses = []
        self.lighting_conditions = []
        self.object_variations = []

    def setup_directories(self):
        """Create output directories for different data types"""
        dirs = [
            f"{self.output_dir}/images",
            f"{self.output_dir}/annotations/semantic",
            f"{self.output_dir}/annotations/instances",
            f"{self.output_dir}/annotations/bboxes",
            f"{self.output_dir}/annotations/depth",
            f"{self.output_dir}/metadata"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def setup_scene(self):
        """Configure the scene with objects and lighting"""
        # Add ground plane
        add_reference_to_stage(
            usd_path="omniverse://localhost/NVIDIA/Assets/Samples/KIT/ground_plane.usd",
            prim_path="/World/GroundPlane"
        )

        # Add lighting
        self.setup_lighting()

        # Add objects to scene
        self.add_objects()

        # Setup camera
        self.setup_camera()

    def setup_lighting(self):
        """Configure realistic lighting conditions"""
        # Add dome light for environment lighting
        dome_light = self.world.scene.add(
            prim_path="/World/DomeLight",
            name="dome_light",
            light_type="DomeLight",
            intensity=3000,
            color=(1.0, 1.0, 1.0)
        )

        # Add directional light for shadows
        directional_light = self.world.scene.add(
            prim_path="/World/DirectionalLight",
            name="directional_light",
            light_type="DistantLight",
            intensity=1500,
            color=(0.9, 0.9, 1.0)
        )

        # Set light direction
        directional_light.set_local_pos([5, 5, 10])

    def add_objects(self):
        """Add objects to the scene with variations"""
        # Example: Add a humanoid robot model
        robot_prim = add_reference_to_stage(
            usd_path="omniverse://localhost/NVIDIA/Assets/Isaac/Robots/Humanoid/humanoid_instanceable.usd",
            prim_path="/World/Robot"
        )

        # Add various objects for training
        objects = [
            ("cup", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/cup.usd"),
            ("box", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/cardboard_box.usd"),
            ("ball", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/small_sphere.usd")
        ]

        for i, (name, usd_path) in enumerate(objects):
            prim_path = f"/World/Object_{name}_{i}"
            obj_prim = add_reference_to_stage(usd_path, prim_path)

            # Randomize position
            x_pos = np.random.uniform(-2, 2)
            y_pos = np.random.uniform(-2, 2)
            z_pos = np.random.uniform(0.1, 1.0)

            obj_prim.set_world_pos([x_pos, y_pos, z_pos])

            # Randomize rotation
            rot_z = np.random.uniform(0, 2 * np.pi)
            obj_prim.set_world_rot([0, 0, rot_z])

    def setup_camera(self):
        """Configure camera for data collection"""
        # Add camera to the scene
        camera = self.world.scene.add(
            prim_path="/World/Camera",
            name="camera",
            translation=[2.0, 2.0, 1.5],
            orientation=[0.0, 0.0, 0.0, 1.0]
        )

        # Configure camera intrinsic parameters
        camera.config_intrinsic_matrix(
            focal_length=24.0,  # mm
            horizontal_aperture=36.0,  # mm
            vertical_aperture=24.0   # mm
        )

        # Set image resolution
        camera.config_image_settings(
            width=640,
            height=480
        )

    def generate_training_data(self):
        """Generate synthetic training data"""
        for sample_idx in range(self.num_samples):
            # Randomize scene
            self.randomize_scene()

            # Simulate physics
            self.world.step(render=True)

            # Capture data
            self.capture_sample(sample_idx)

            print(f"Generated sample {sample_idx + 1}/{self.num_samples}")

    def randomize_scene(self):
        """Randomize scene parameters for diversity"""
        # Randomize lighting
        dome_intensity = np.random.uniform(1000, 5000)
        directional_intensity = np.random.uniform(1000, 3000)

        # Randomize camera position
        camera_x = np.random.uniform(1, 3)
        camera_y = np.random.uniform(1, 3)
        camera_z = np.random.uniform(1, 2)

        # Apply randomizations
        self.world.scene.get_object("dome_light").set_attribute("inputs:intensity", dome_intensity)
        self.world.scene.get_object("directional_light").set_attribute("inputs:intensity", directional_intensity)

        camera = self.world.scene.get_object("camera")
        camera.set_world_pos([camera_x, camera_y, camera_z])

        # Randomize object positions and orientations
        for i in range(3):  # 3 objects added earlier
            obj_name = f"KIT_{['cup', 'box', 'ball'][i]}_{i}"
            if self.world.scene.has_object(obj_name):
                obj = self.world.scene.get_object(obj_name)

                # Randomize position
                dx = np.random.uniform(-0.5, 0.5)
                dy = np.random.uniform(-0.5, 0.5)
                dz = np.random.uniform(-0.2, 0.2)

                pos = obj.get_world_pos()
                obj.set_world_pos([pos[0] + dx, pos[1] + dy, max(0.1, pos[2] + dz)])

                # Randomize rotation
                rot_z = np.random.uniform(0, 2 * np.pi)
                obj.set_world_rot([0, 0, rot_z])

    def capture_sample(self, sample_idx):
        """Capture a complete sample with all annotations"""
        # Get camera
        camera = self.world.scene.get_object("camera")

        # Capture RGB image
        rgb_image = camera.get_rgb()
        rgb_filename = f"{self.output_dir}/images/{sample_idx:06d}.png"
        cv2.imwrite(rgb_filename, cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))

        # Capture semantic segmentation
        semantic_image = camera.get_semantic_segmentation()
        semantic_filename = f"{self.output_dir}/annotations/semantic/{sample_idx:06d}.png"
        cv2.imwrite(semantic_filename, semantic_image)

        # Capture instance segmentation
        instance_image = camera.get_instance_segmentation()
        instance_filename = f"{self.output_dir}/annotations/instances/{sample_idx:06d}.png"
        cv2.imwrite(instance_filename, instance_image)

        # Capture depth map
        depth_image = camera.get_depth()
        depth_filename = f"{self.output_dir}/annotations/depth/{sample_idx:06d}.exr"
        cv2.imwrite(depth_filename, depth_image)

        # Generate bounding box annotations
        bbox_annotations = self.generate_bbox_annotations(instance_image)
        bbox_filename = f"{self.output_dir}/annotations/bboxes/{sample_idx:06d}.json"
        self.save_annotations(bbox_annotations, bbox_filename)

        # Save metadata
        metadata = {
            'sample_id': sample_idx,
            'timestamp': self.world.current_time,
            'camera_pose': camera.get_world_pose(),
            'lighting_condition': {
                'dome_intensity': self.world.scene.get_object("dome_light").get_attribute("inputs:intensity"),
                'directional_intensity': self.world.scene.get_object("directional_light").get_attribute("inputs:intensity")
            }
        }

        meta_filename = f"{self.output_dir}/metadata/{sample_idx:06d}.json"
        self.save_metadata(metadata, meta_filename)

    def generate_bbox_annotations(self, instance_image):
        """Generate bounding box annotations from instance segmentation"""
        import json

        # Find unique instances in the image
        unique_instances = np.unique(instance_image)

        annotations = []
        for instance_id in unique_instances:
            if instance_id == 0:  # Background
                continue

            # Create mask for this instance
            mask = (instance_image == instance_id).astype(np.uint8)

            # Find contours to get bounding box
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                annotation = {
                    'instance_id': int(instance_id),
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'area': int(cv2.contourArea(largest_contour)),
                    'centroid': [int(x + w/2), int(y + h/2)]
                }
                annotations.append(annotation)

        return annotations

    def save_annotations(self, annotations, filename):
        """Save annotation data to JSON file"""
        import json
        with open(filename, 'w') as f:
            json.dump(annotations, f, indent=2)

    def save_metadata(self, metadata, filename):
        """Save metadata to JSON file"""
        import json
        with open(filename, 'w') as f:
            json.dump(metadata, f, indent=2)

    def run_data_generation(self):
        """Execute the complete data generation pipeline"""
        print("Setting up scene...")
        self.setup_scene()

        print("Generating training data...")
        self.generate_training_data()

        print(f"Data generation complete! Output saved to {self.output_dir}")

        # Cleanup
        self.world.clear()

# Example usage
if __name__ == "__main__":
    generator = IsaacSimDataGenerator(output_dir="my_synthetic_dataset", num_samples=100)
    generator.run_data_generation()
```

## Domain Randomization

Domain randomization is crucial for synthetic-to-real transfer:

### Color and Material Randomization

```python
def randomize_materials(self):
    """Randomize materials and colors for domain randomization"""
    # Get all objects in the scene
    objects = self.world.scene.get_objects()

    for obj_name, obj in objects.items():
        if hasattr(obj, 'prim'):  # Check if it's a valid prim
            # Randomize color
            color = [
                np.random.uniform(0.1, 1.0),  # Red
                np.random.uniform(0.1, 1.0),  # Green
                np.random.uniform(0.1, 1.0)   # Blue
            ]

            # Randomize material properties
            roughness = np.random.uniform(0.1, 0.9)
            metallic = np.random.uniform(0.0, 0.5)

            # Apply randomization
            self.apply_material_properties(obj.prim, color, roughness, metallic)

def apply_material_properties(self, prim, color, roughness, metallic):
    """Apply randomized material properties to a prim"""
    from pxr import UsdShade

    # Create material
    material_path = f"{prim.GetPath()}/Material"
    material = UsdShade.Material.Define(self.world.stage, material_path)

    # Create PBR shader
    shader = UsdShade.Shader.Define(self.world.stage, f"{material_path}/Shader")
    shader.CreateIdAttr("UsdPreviewSurface")

    # Set material properties
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(metallic)

    # Bind material to prim
    UsdShade.MaterialBindingAPI(prim).Bind(material)
```

### Environmental Randomization

```python
def randomize_environment(self):
    """Randomize environmental conditions"""
    # Randomize time of day (affects lighting)
    hour = np.random.uniform(0, 24)
    self.set_time_of_day(hour)

    # Randomize weather conditions
    weather = np.random.choice(['clear', 'overcast', 'rainy', 'snowy'])
    self.set_weather_conditions(weather)

    # Randomize camera parameters
    self.randomize_camera_parameters()

    # Randomize object textures
    self.randomize_object_textures()

def set_time_of_day(self, hour):
    """Set time of day to affect lighting"""
    # Calculate sun position based on time
    sun_angle = (hour / 24.0) * 2 * np.pi  # Full circle over 24 hours
    sun_elevation = np.sin(sun_angle) * 0.8 + 0.2  # Keep sun above horizon
    sun_azimuth = np.cos(sun_angle)

    # Update directional light based on sun position
    sun_pos = [
        sun_azimuth * 10,
        sun_elevation * 10,
        10
    ]

    directional_light = self.world.scene.get_object("directional_light")
    if directional_light:
        directional_light.set_world_pos(sun_pos)

def set_weather_conditions(self, weather_type):
    """Set weather conditions for environmental variation"""
    if weather_type == 'overcast':
        # Reduce lighting intensity
        self.world.scene.get_object("dome_light").set_attribute("inputs:intensity", 1000)
        self.world.scene.get_object("directional_light").set_attribute("inputs:intensity", 500)
    elif weather_type == 'rainy':
        # Add atmospheric effects
        self.add_rain_effects()
    elif weather_type == 'snowy':
        # Add snow effects
        self.add_snow_effects()
    else:  # clear
        # Standard lighting
        self.world.scene.get_object("dome_light").set_attribute("inputs:intensity", 3000)
        self.world.scene.get_object("directional_light").set_attribute("inputs:intensity", 1500)
```

## Annotation Generation

### Semantic Segmentation

```python
def generate_semantic_annotations(self, rgb_image_shape):
    """Generate semantic segmentation annotations"""
    # Semantic segmentation assigns class labels to each pixel
    semantic_map = np.zeros(rgb_image_shape[:2], dtype=np.uint8)

    # Get instance segmentation to map instances to semantic classes
    instance_map = self.get_current_instance_map()

    # Define class mapping
    class_mapping = {
        1: 0,   # Background
        2: 1,   # Robot
        3: 2,   # Cup
        4: 3,   # Box
        5: 4,   # Ball
        # Add more mappings as needed
    }

    # Convert instance IDs to semantic classes
    for instance_id in np.unique(instance_map):
        if instance_id in class_mapping:
            semantic_class = class_mapping[instance_id]
            semantic_map[instance_map == instance_id] = semantic_class

    return semantic_map

def generate_instance_annotations(self, rgb_image_shape):
    """Generate instance segmentation annotations"""
    # Instance segmentation distinguishes individual object instances
    instance_map = np.zeros(rgb_image_shape[:2], dtype=np.uint32)

    # Get all objects in the scene
    objects = self.world.scene.get_objects()

    instance_id = 1
    for obj_name, obj in objects.items():
        if hasattr(obj, 'prim') and obj.is_visible():
            # Render object to get its mask
            mask = self.render_object_mask(obj)
            instance_map[mask > 0] = instance_id
            instance_id += 1

    return instance_map.astype(np.uint8)
```

### 3D Bounding Boxes and Keypoints

```python
def generate_3d_bounding_boxes(self):
    """Generate 3D bounding box annotations"""
    boxes_3d = []

    objects = self.world.scene.get_objects()
    camera = self.world.scene.get_object("camera")

    for obj_name, obj in objects.items():
        if hasattr(obj, 'prim') and obj.is_visible():
            # Get object's 3D bounding box in world coordinates
            bbox_3d = obj.get_world_bounding_box()

            # Project 3D bounding box to 2D image coordinates
            corners_2d = []
            for corner in bbox_3d.corners:
                projected = self.project_3d_to_2d(corner, camera)
                corners_2d.append(projected)

            # Calculate 2D bounding box from projected corners
            xs = [p[0] for p in corners_2d]
            ys = [p[1] for p in corners_2d]

            bbox_2d = {
                'x_min': min(xs),
                'y_min': min(ys),
                'x_max': max(xs),
                'y_max': max(ys),
                'object_name': obj_name,
                'confidence': 1.0  # Perfect confidence in simulation
            }

            boxes_3d.append({
                'bbox_3d': bbox_3d,
                'bbox_2d': bbox_2d,
                'object_class': self.get_object_class(obj_name)
            })

    return boxes_3d

def generate_keypoints_annotations(self):
    """Generate 3D keypoint annotations for humanoid robots"""
    keypoints = []

    # For humanoid robots, generate joint keypoints
    robot = self.world.scene.get_object("robot")  # Assuming humanoid robot exists
    if robot:
        joint_names = [
            'pelvis', 'left_hip', 'left_knee', 'left_ankle',
            'right_hip', 'right_knee', 'right_ankle',
            'torso', 'neck', 'head',
            'left_shoulder', 'left_elbow', 'left_wrist',
            'right_shoulder', 'right_elbow', 'right_wrist'
        ]

        for joint_name in joint_names:
            # Get joint position in world coordinates
            joint_pos = robot.get_joint_position(joint_name)

            # Project to 2D image coordinates
            camera = self.world.scene.get_object("camera")
            pos_2d = self.project_3d_to_2d(joint_pos, camera)

            keypoint = {
                'name': joint_name,
                'position_3d': joint_pos.tolist(),
                'position_2d': pos_2d,
                'visibility': self.is_keypoint_visible(joint_pos, camera)
            }

            keypoints.append(keypoint)

    return keypoints

def project_3d_to_2d(self, point_3d, camera):
    """Project 3D point to 2D image coordinates"""
    # Get camera intrinsic and extrinsic parameters
    intrinsics = camera.get_intrinsics()
    extrinsics = camera.get_extrinsics()

    # Transform point from world to camera coordinates
    point_cam = np.dot(extrinsics['rotation'], point_3d) + extrinsics['translation']

    # Project to image plane
    x_proj = point_cam[0] / point_cam[2]  # Perspective division
    y_proj = point_cam[1] / point_cam[2]

    # Apply intrinsic parameters
    u = intrinsics['fx'] * x_proj + intrinsics['cx']
    v = intrinsics['fy'] * y_proj + intrinsics['cy']

    return [int(u), int(v)]

def is_keypoint_visible(self, point_3d, camera):
    """Check if a 3D point is visible in the camera"""
    # Project point to 2D
    pos_2d = self.project_3d_to_2d(point_3d, camera)

    # Check if within image bounds
    img_width, img_height = camera.get_resolution()
    u, v = pos_2d

    if 0 <= u < img_width and 0 <= v < img_height:
        # Check depth to ensure not occluded
        depth_at_point = self.get_depth_at_pixel(u, v)
        actual_depth = np.linalg.norm(point_3d - camera.get_world_pos())

        # Point is visible if its depth matches the rendered depth (within tolerance)
        return abs(depth_at_point - actual_depth) < 0.1
    else:
        return False
```

## Data Quality Validation

### Quality Assessment Metrics

```python
class DataQualityValidator:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def validate_data_quality(self):
        """Validate the quality of generated synthetic data"""
        metrics = {}

        # Validate image quality
        metrics['image_quality'] = self.validate_image_quality()

        # Validate annotation accuracy
        metrics['annotation_quality'] = self.validate_annotations()

        # Validate diversity
        metrics['diversity'] = self.validate_diversity()

        # Validate realism
        metrics['realism_score'] = self.validate_realism()

        return metrics

    def validate_image_quality(self):
        """Validate basic image quality metrics"""
        import cv2

        image_dir = os.path.join(self.dataset_path, 'images')
        image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]

        quality_metrics = {
            'sharpness': [],
            'brightness': [],
            'contrast': [],
            'noise_level': []
        }

        for img_file in image_files[:100]:  # Sample first 100 for efficiency
            img_path = os.path.join(image_dir, img_file)
            img = cv2.imread(img_path)

            # Calculate sharpness using Laplacian variance
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'].append(laplacian_var)

            # Calculate brightness
            brightness = np.mean(gray)
            quality_metrics['brightness'].append(brightness)

            # Calculate contrast
            contrast = np.std(gray)
            quality_metrics['contrast'].append(contrast)

            # Calculate noise (high frequency content)
            noise = self.estimate_noise(gray)
            quality_metrics['noise_level'].append(noise)

        # Calculate statistics
        results = {}
        for metric, values in quality_metrics.items():
            results[f'{metric}_mean'] = np.mean(values)
            results[f'{metric}_std'] = np.std(values)
            results[f'{metric}_range'] = (np.min(values), np.max(values))

        return results

    def estimate_noise(self, image):
        """Estimate noise level in image"""
        # Use wavelet decomposition or high-pass filtering
        # Simplified version using high-frequency content
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        noise = np.mean(np.abs(image.astype(float) - blurred.astype(float)))
        return noise

    def validate_annotations(self):
        """Validate annotation quality"""
        # Check annotation completeness
        # Validate bounding box consistency
        # Verify segmentation accuracy
        pass

    def validate_diversity(self):
        """Validate dataset diversity"""
        # Analyze distribution of scenes, objects, lighting conditions
        # Check for balanced class distribution
        # Validate variation in poses and viewpoints
        pass

    def validate_realism(self):
        """Validate realism of synthetic data"""
        # Compare statistical properties to real data
        # Use domain adaptation metrics
        # Validate perceptual quality
        pass
```

## Integration with ML Workflows

### Dataset Format Compatibility

```python
class DatasetFormatter:
    """Format synthetic data for different ML frameworks"""

    def to_coco_format(self, source_dir, output_dir):
        """Convert to COCO dataset format"""
        import json

        coco_dataset = {
            "info": {
                "description": "Synthetic Humanoid Robot Dataset",
                "version": "1.0",
                "year": 2025,
                "contributor": "Isaac Sim Synthetic Data Generator",
                "date_created": "2025/01/01"
            },
            "licenses": [{"id": 1, "name": "Synthetic Data License", "url": ""}],
            "categories": [
                {"id": 1, "name": "robot", "supercategory": "robot"},
                {"id": 2, "name": "cup", "supercategory": "object"},
                {"id": 3, "name": "box", "supercategory": "object"},
                {"id": 4, "name": "ball", "supercategory": "object"}
            ],
            "images": [],
            "annotations": []
        }

        # Process each image
        image_dir = os.path.join(source_dir, "images")
        for i, img_file in enumerate(os.listdir(image_dir)):
            img_path = os.path.join(image_dir, img_file)
            img = cv2.imread(img_path)

            image_info = {
                "id": i,
                "file_name": img_file,
                "width": img.shape[1],
                "height": img.shape[0],
                "date_captured": "2025-01-01",
                "license": 1,
                "flickr_url": "",
                "coco_url": "",
                "id": i
            }
            coco_dataset["images"].append(image_info)

        # Save COCO dataset
        output_path = os.path.join(output_dir, "annotations.json")
        with open(output_path, 'w') as f:
            json.dump(coco_dataset, f, indent=2)

    def to_yolo_format(self, source_dir, output_dir):
        """Convert to YOLO dataset format"""
        # YOLO format: class_id center_x center_y width height (normalized)
        pass

    def to_tfrecord_format(self, source_dir, output_dir):
        """Convert to TensorFlow Record format"""
        # TFRecord format for TensorFlow/PyTorch training
        pass
```

## Best Practices for Synthetic Data Generation

### Quality Assurance

1. **Validation Against Real Data**: Compare synthetic statistics to real data
2. **Domain Randomization**: Apply sufficient variation for robustness
3. **Annotation Accuracy**: Ensure perfect ground truth annotations
4. **Diversity**: Cover all possible scenarios and edge cases
5. **Realism**: Maintain photorealistic quality for transfer learning
6. **Scalability**: Generate sufficient data for training requirements

### Performance Optimization

1. **Batch Processing**: Process multiple samples in parallel
2. **GPU Acceleration**: Utilize GPU for rendering and processing
3. **Memory Management**: Efficiently manage memory during generation
4. **Storage Optimization**: Use appropriate compression and formats
5. **Progress Monitoring**: Track generation progress and quality

This comprehensive synthetic data generation system provides the foundation for training robust perception systems in humanoid robots, enabling the development of vision-language-action capabilities with minimal real-world data requirements.