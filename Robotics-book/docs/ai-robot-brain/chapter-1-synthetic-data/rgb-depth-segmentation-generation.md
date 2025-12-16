---
sidebar_position: 3
---

# RGB/Depth/Segmentation Data Generation

## Creating Photorealistic Training Data for Computer Vision

Generating high-quality RGB, depth, and segmentation data is crucial for training robust computer vision systems for humanoid robots. This chapter covers the generation of synthetic datasets with photorealistic quality and perfect annotations for perception system training.

## Learning Objectives

By the end of this chapter, you will:
- Generate photorealistic RGB images with realistic lighting and materials
- Create accurate depth maps for 3D scene understanding
- Generate pixel-perfect semantic and instance segmentation masks
- Apply domain randomization for robust model training
- Validate synthetic data quality for real-world transfer
- Optimize data generation pipelines for efficiency

## RGB Image Generation

### Photorealistic Rendering Pipeline

```python
# rgb_generation.py
import omni
from omni.isaac.core import World
from omni.isaac.synthetic_utils import SyntheticDataHelper
from omni.isaac.core.utils.stage import add_reference_to_stage
import carb
import numpy as np
import cv2
from PIL import Image
import os
import json
from typing import List, Tuple, Dict, Optional

class RGBGenerator:
    def __init__(self, output_dir: str = "synthetic_rgb_data", num_samples: int = 1000):
        self.output_dir = output_dir
        self.num_samples = num_samples

        # Setup output directories
        self.setup_directories()

        # Initialize Isaac Sim world
        self.world = World(stage_units_in_meters=1.0)
        self.sd_helper = SyntheticDataHelper()

        # Camera configuration
        self.camera_resolution = (1280, 720)  # HD resolution
        self.camera_fov = 60.0  # Field of view in degrees
        self.camera_position = [2.0, 2.0, 1.5]  # Default camera position

        # Scene configuration
        self.objects = []
        self.lighting_conditions = []
        self.material_variations = []

    def setup_directories(self):
        """Create necessary output directories"""
        dirs = [
            f"{self.output_dir}/images",
            f"{self.output_dir}/metadata",
            f"{self.output_dir}/lighting_configs",
            f"{self.output_dir}/material_configs"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def setup_scene(self):
        """Setup the initial scene with objects and lighting"""
        # Add ground plane
        ground_path = "/World/GroundPlane"
        add_reference_to_stage(
            usd_path="omniverse://localhost/NVIDIA/Assets/Isaac/Props/Grid/default_grid.usd",
            prim_path=ground_path
        )

        # Add basic lighting
        self.setup_lighting()

        # Add objects to scene
        self.add_training_objects()

        # Setup camera
        self.setup_camera()

    def setup_lighting(self):
        """Configure realistic lighting conditions"""
        # Add dome light for ambient lighting
        carb.settings.get_settings().set("/lights/defaultDomeLightColor", [0.2, 0.2, 0.2])
        carb.settings.get_settings().set("/lights/defaultDomeLightIntensity", 3000)

        # Add directional light for shadows
        carb.settings.get_settings().set("/lights/defaultDistantLightColor", [0.9, 0.9, 0.9])
        carb.settings.get_settings().set("/lights/defaultDistantLightIntensity", 1500)

    def add_training_objects(self):
        """Add objects for training data generation"""
        # Define common household objects for humanoid robot training
        training_objects = [
            ("cup", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/cup.usd", [0.5, 0.0, 0.05]),
            ("book", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/book.usd", [0.0, 0.5, 0.05]),
            ("ball", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/small_sphere.usd", [-0.5, 0.0, 0.05]),
            ("box", "omniverse://localhost/NVIDIA/Assets/Isaac/Props/KIT/cardboard_box.usd", [0.0, -0.5, 0.05])
        ]

        for i, (name, usd_path, position) in enumerate(training_objects):
            prim_path = f"/World/Object_{name}_{i}"
            try:
                add_reference_to_stage(usd_path, prim_path)

                # Get the object and set its position
                obj = self.world.scene.get_object(f"Object_{name}_{i}")
                if obj:
                    obj.set_world_pos(position)

                self.objects.append({
                    'name': name,
                    'prim_path': prim_path,
                    'base_position': position
                })
            except Exception as e:
                print(f"Failed to add object {name}: {e}")

    def setup_camera(self):
        """Configure camera for RGB image capture"""
        # Add camera to the scene
        from omni.isaac.core.prims import XFormPrim
        camera_prim = XFormPrim("/World/Camera", position=self.camera_position)

        # Configure camera properties
        carb.settings.get_settings().set("/camera/defaultResolution/width", self.camera_resolution[0])
        carb.settings.get_settings().set("/camera/defaultResolution/height", self.camera_resolution[1])
        carb.settings.get_settings().set("/camera/defaultFov", self.camera_fov)

    def generate_photorealistic_images(self):
        """Generate photorealistic RGB images with variations"""
        for sample_idx in range(self.num_samples):
            # Randomize scene for this sample
            self.randomize_scene(sample_idx)

            # Step simulation to update scene
            self.world.step(render=True)

            # Capture RGB image
            rgb_image = self.capture_rgb_image()

            # Apply realistic effects
            rgb_image = self.apply_realistic_effects(rgb_image, sample_idx)

            # Save image
            image_path = f"{self.output_dir}/images/{sample_idx:06d}.png"
            Image.fromarray(rgb_image).save(image_path)

            # Save metadata
            metadata = self.generate_metadata(sample_idx)
            metadata_path = f"{self.output_dir}/metadata/{sample_idx:06d}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            if sample_idx % 100 == 0:
                print(f"Generated {sample_idx + 1}/{self.num_samples} RGB images")

    def randomize_scene(self, sample_idx: int):
        """Randomize scene parameters for diversity"""
        # Randomize lighting
        dome_intensity = np.random.uniform(1000, 5000)
        directional_intensity = np.random.uniform(500, 2000)
        carb.settings.get_settings().set("/lights/defaultDomeLightIntensity", dome_intensity)
        carb.settings.get_settings().set("/lights/defaultDistantLightIntensity", directional_intensity)

        # Randomize camera position
        camera_x = np.random.uniform(1.0, 3.0)
        camera_y = np.random.uniform(1.0, 3.0)
        camera_z = np.random.uniform(1.0, 2.0)
        camera_pos = [camera_x, camera_y, camera_z]

        # Randomize camera orientation
        camera_yaw = np.random.uniform(-np.pi, np.pi)
        camera_pitch = np.random.uniform(-np.pi/4, np.pi/4)
        camera_roll = np.random.uniform(-np.pi/12, np.pi/12)

        # Apply camera transformation
        from scipy.spatial.transform import Rotation as R
        rot_matrix = R.from_euler('xyz', [camera_roll, camera_pitch, camera_yaw]).as_matrix()

        # Update camera in scene
        camera_prim = self.world.scene.get_object("Camera")
        if camera_prim:
            camera_prim.set_world_pos(camera_pos)
            # Set orientation (simplified)

        # Randomize object positions
        for obj_info in self.objects:
            obj = self.world.scene.get_object(obj_info['name'])
            if obj:
                # Add random offset to base position
                rand_offset = [
                    np.random.uniform(-0.3, 0.3),
                    np.random.uniform(-0.3, 0.3),
                    np.random.uniform(0, 0.1)  # Only positive Z offset
                ]
                new_pos = [
                    obj_info['base_position'][0] + rand_offset[0],
                    obj_info['base_position'][1] + rand_offset[1],
                    obj_info['base_position'][2] + rand_offset[2]
                ]
                obj.set_world_pos(new_pos)

    def capture_rgb_image(self):
        """Capture RGB image from the configured camera"""
        # This would interface with Isaac Sim's rendering system
        # In practice, you'd use the SyntheticDataHelper to get RGB data

        # Simulated RGB capture (replace with actual Isaac Sim call)
        width, height = self.camera_resolution
        # Create a simulated image with basic colors and shapes
        rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

        # Add some simulated content for demonstration
        for i in range(height):
            for j in range(width):
                # Simulate gradient and basic shapes
                rgb_image[i, j, 0] = int(100 + 50 * np.sin(i / 50))  # Red channel
                rgb_image[i, j, 1] = int(100 + 50 * np.cos(j / 50))  # Green channel
                rgb_image[i, j, 2] = int(150 + 30 * np.sin((i+j) / 100))  # Blue channel

        return rgb_image

    def apply_realistic_effects(self, image: np.ndarray, sample_idx: int) -> np.ndarray:
        """Apply realistic effects to make images more photorealistic"""
        # Apply lens distortion
        image = self.apply_lens_distortion(image)

        # Add realistic noise
        image = self.add_realistic_noise(image)

        # Apply chromatic aberration
        image = self.apply_chromatic_aberration(image)

        # Adjust color grading
        image = self.adjust_color_grading(image, sample_idx)

        # Add motion blur (if objects are moving)
        image = self.apply_motion_blur(image)

        return image

    def apply_lens_distortion(self, image: np.ndarray) -> np.ndarray:
        """Apply lens distortion to simulate real camera effects"""
        h, w = image.shape[:2]

        # Define distortion coefficients
        k1, k2 = np.random.uniform(-0.1, 0.1, 2)  # Radial distortion
        p1, p2 = np.random.uniform(-0.01, 0.01, 2)  # Tangential distortion

        # Create coordinate grids
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        x_grid, y_grid = np.meshgrid(x, y)

        # Calculate distorted coordinates
        r_squared = x_grid**2 + y_grid**2
        radial_distortion = 1 + k1 * r_squared + k2 * r_squared**2
        x_distorted = x_grid * radial_distortion + 2*p1*x_grid*y_grid + p2*(r_squared + 2*x_grid**2)
        y_distorted = y_grid * radial_distortion + p1*(r_squared + 2*y_grid**2) + 2*p2*x_grid*y_grid

        # Normalize back to image coordinates
        x_distorted = ((x_distorted + 1) / 2) * (w - 1)
        y_distorted = ((y_distorted + 1) / 2) * (h - 1)

        # Remap image
        remapped = np.zeros_like(image)
        for c in range(3):  # For each color channel
            remapped[:, :, c] = cv2.remap(
                image[:, :, c],
                x_distorted.astype(np.float32),
                y_distorted.astype(np.float32),
                interpolation=cv2.INTER_LINEAR
            )

        return remapped

    def add_realistic_noise(self, image: np.ndarray) -> np.ndarray:
        """Add realistic camera noise"""
        # Add different types of noise
        h, w = image.shape[:2]

        # Photon shot noise (signal-dependent)
        signal_noise = np.random.poisson(image.astype(np.float32))
        signal_noise = np.clip(signal_noise, 0, 255).astype(np.uint8)

        # Read noise (signal-independent)
        read_noise = np.random.normal(0, np.random.uniform(2, 8), image.shape).astype(np.int16)

        # Combine noises
        noisy_image = image.astype(np.int16) + (signal_noise.astype(np.int16) - image.astype(np.int16)) + read_noise
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

        return noisy_image

    def apply_chromatic_aberration(self, image: np.ndarray) -> np.ndarray:
        """Apply chromatic aberration to simulate lens imperfections"""
        h, w = image.shape[:2]

        # Create radial coordinate
        center_x, center_y = w // 2, h // 2
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        r = np.sqrt((x - center_x)**2 + (y - center_y)**2) / max(center_x, center_y)

        # Apply different scaling to color channels
        scale_factors = np.random.uniform(0.999, 1.001, 3)  # R, G, B channels

        result = np.zeros_like(image)
        for c in range(3):
            # Scale the channel
            scaled_coords_x = center_x + (x - center_x) * scale_factors[c]
            scaled_coords_y = center_y + (y - center_y) * scale_factors[c]

            # Remap using bilinear interpolation
            result[:, :, c] = cv2.remap(
                image[:, :, c],
                scaled_coords_x.astype(np.float32),
                scaled_coords_y.astype(np.float32),
                interpolation=cv2.INTER_LINEAR
            )

        return result

    def adjust_color_grading(self, image: np.ndarray, sample_idx: int) -> np.ndarray:
        """Apply color grading based on lighting conditions"""
        # Adjust color temperature based on lighting
        lighting_condition = sample_idx % 4  # 4 different lighting conditions

        # Define color adjustments for different lighting
        color_adjustments = [
            [1.0, 1.0, 1.0],      # Normal lighting
            [1.1, 1.0, 0.9],      # Warm lighting (incandescent)
            [0.9, 0.95, 1.1],     # Cool lighting (fluorescent)
            [1.2, 1.1, 0.9]       # Sunset lighting
        ]

        adjustment = np.array(color_adjustments[lighting_condition])

        # Apply color grading
        adjusted = image.astype(np.float32) * adjustment
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)

        return adjusted

    def apply_motion_blur(self, image: np.ndarray) -> np.ndarray:
        """Apply motion blur to simulate camera/object movement"""
        # Randomly apply motion blur
        if np.random.random() < 0.1:  # 10% chance
            kernel_size = np.random.randint(3, 7)
            angle = np.random.uniform(0, 360)

            # Create motion blur kernel
            kernel = np.zeros((kernel_size, kernel_size))
            kernel[kernel_size//2, :] = 1
            kernel = cv2.warpAffine(kernel, cv2.getRotationMatrix2D((kernel_size//2, kernel_size//2), angle, 1), (kernel_size, kernel_size))
            kernel = kernel / kernel.sum()

            # Apply motion blur
            blurred = cv2.filter2D(image, -1, kernel)
            return blurred

        return image

    def generate_metadata(self, sample_idx: int) -> Dict:
        """Generate metadata for the RGB image"""
        metadata = {
            'sample_id': sample_idx,
            'timestamp': carb.events.acquire_application_interface().get_application().get_time(),
            'camera_config': {
                'resolution': self.camera_resolution,
                'fov': self.camera_fov,
                'position': self.camera_position
            },
            'lighting_config': {
                'dome_intensity': carb.settings.get_settings().get("/lights/defaultDomeLightIntensity"),
                'directional_intensity': carb.settings.get_settings().get("/lights/defaultDistantLightIntensity")
            },
            'object_positions': [obj['base_position'] for obj in self.objects],
            'distortion_coefficients': {
                'k1': np.random.uniform(-0.1, 0.1),
                'k2': np.random.uniform(-0.1, 0.1),
                'p1': np.random.uniform(-0.01, 0.01),
                'p2': np.random.uniform(-0.01, 0.01)
            },
            'noise_parameters': {
                'photon_noise_factor': np.random.uniform(0.8, 1.2),
                'read_noise_sigma': np.random.uniform(2, 8)
            }
        }

        return metadata

    def run_generation(self):
        """Execute the complete RGB generation pipeline"""
        print("Setting up scene for RGB generation...")
        self.setup_scene()

        print(f"Generating {self.num_samples} photorealistic RGB images...")
        self.generate_photorealistic_images()

        print(f"RGB generation complete! Output saved to {self.output_dir}")

        # Cleanup
        self.world.clear()

# Example usage
if __name__ == "__main__":
    generator = RGBGenerator(output_dir="my_rgb_dataset", num_samples=500)
    generator.run_generation()
```

## Depth Map Generation

### Accurate Depth Information

```python
# depth_generation.py
import numpy as np
import cv2
from PIL import Image
import json
import os
from typing import Tuple, Dict, List

class DepthGenerator:
    def __init__(self, output_dir: str = "synthetic_depth_data", num_samples: int = 1000):
        self.output_dir = output_dir
        self.num_samples = num_samples

        # Setup output directories
        self.setup_directories()

        # Camera intrinsic parameters
        self.fx = 640.0  # Focal length x
        self.fy = 640.0  # Focal length y
        self.cx = 320.0  # Principal point x
        self.cy = 240.0  # Principal point y

        # Depth range parameters
        self.min_depth = 0.1  # meters
        self.max_depth = 10.0  # meters

        # Resolution
        self.width = 640
        self.height = 480

    def setup_directories(self):
        """Create necessary output directories"""
        dirs = [
            f"{self.output_dir}/depth_maps",
            f"{self.output_dir}/depth_metadata",
            f"{self.output_dir}/point_clouds"  # For 3D reconstruction
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def generate_depth_maps(self):
        """Generate synthetic depth maps"""
        for sample_idx in range(self.num_samples):
            # Create a synthetic depth map
            depth_map = self.create_synthetic_depth_map(sample_idx)

            # Apply realistic depth noise
            depth_map = self.apply_depth_noise(depth_map, sample_idx)

            # Save depth map
            depth_path = f"{self.output_dir}/depth_maps/{sample_idx:06d}.exr"
            self.save_depth_map(depth_map, depth_path)

            # Save metadata
            metadata = self.generate_depth_metadata(sample_idx, depth_map)
            metadata_path = f"{self.output_dir}/depth_metadata/{sample_idx:06d}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            if sample_idx % 100 == 0:
                print(f"Generated {sample_idx + 1}/{self.num_samples} depth maps")

    def create_synthetic_depth_map(self, sample_idx: int) -> np.ndarray:
        """Create a synthetic depth map with realistic scene structures"""
        depth_map = np.ones((self.height, self.width), dtype=np.float32) * self.max_depth

        # Add some geometric shapes to simulate objects
        center_x, center_y = self.width // 2, self.height // 2

        # Add a central object (like a cube)
        cube_size = np.random.uniform(50, 150)
        cube_depth = np.random.uniform(self.min_depth, self.max_depth * 0.8)

        x_min = max(0, int(center_x - cube_size/2))
        x_max = min(self.width, int(center_x + cube_size/2))
        y_min = max(0, int(center_y - cube_size/2))
        y_max = min(self.height, int(center_y + cube_size/2))

        depth_map[y_min:y_max, x_min:x_max] = cube_depth

        # Add some random objects
        num_objects = np.random.randint(3, 8)
        for _ in range(num_objects):
            obj_x = np.random.randint(50, self.width - 50)
            obj_y = np.random.randint(50, self.height - 50)
            obj_radius = np.random.uniform(10, 40)
            obj_depth = np.random.uniform(self.min_depth, self.max_depth * 0.9)

            # Create circular object
            y, x = np.ogrid[:self.height, :self.width]
            mask = (x - obj_x)**2 + (y - obj_y)**2 <= obj_radius**2
            depth_map[mask] = np.minimum(depth_map[mask], obj_depth)

        # Add ground plane
        ground_depth = np.random.uniform(self.max_depth * 0.9, self.max_depth)
        depth_map = np.minimum(depth_map, ground_depth)

        return depth_map

    def apply_depth_noise(self, depth_map: np.ndarray, sample_idx: int) -> np.ndarray:
        """Apply realistic depth sensor noise"""
        # Calculate noise based on depth (range-dependent noise)
        # For stereo cameras: noise increases quadratically with depth
        # For ToF cameras: noise increases linearly with depth
        # For structured light: relatively constant noise

        camera_type = np.random.choice(['stereo', 'tof', 'structured_light'])

        if camera_type == 'stereo':
            # Stereo camera noise: quadratic with depth
            noise_factor = 0.001  # Base noise factor
            depth_dependent_noise = noise_factor * depth_map**2
        elif camera_type == 'tof':
            # Time-of-flight noise: linear with depth
            noise_factor = 0.002
            depth_dependent_noise = noise_factor * depth_map
        else:  # structured_light
            # Structured light: relatively constant noise
            noise_factor = 0.01
            depth_dependent_noise = np.full_like(depth_map, noise_factor * self.max_depth)

        # Add random noise
        random_noise = np.random.normal(0, depth_dependent_noise)

        # Apply noise
        noisy_depth = depth_map + random_noise

        # Clamp to valid range
        noisy_depth = np.clip(noisy_depth, self.min_depth, self.max_depth)

        # Add quantization noise for digital sensors
        quantization_levels = 2**16  # 16-bit precision
        noisy_depth = np.round(noisy_depth * quantization_levels) / quantization_levels

        return noisy_depth

    def save_depth_map(self, depth_map: np.ndarray, filepath: str):
        """Save depth map in EXR format for high precision"""
        # Convert to 3-channel for EXR (OpenEXR requirement)
        # Actually, for depth we can save as single channel
        from PIL import Image
        import struct

        # For simplicity, save as 16-bit PNG with scaling
        # In practice, use OpenEXR for true floating-point precision
        scaled_depth = (depth_map - self.min_depth) / (self.max_depth - self.min_depth)
        scaled_depth = np.clip(scaled_depth, 0, 1)
        scaled_depth = (scaled_depth * 65535).astype(np.uint16)

        # Save as 16-bit PNG
        Image.fromarray(scaled_depth).save(filepath.replace('.exr', '.png'))

    def generate_depth_metadata(self, sample_idx: int, depth_map: np.ndarray) -> Dict:
        """Generate metadata for depth map"""
        # Calculate statistics
        valid_pixels = depth_map[depth_map > self.min_depth]
        avg_depth = np.mean(valid_pixels) if len(valid_pixels) > 0 else 0
        std_depth = np.std(valid_pixels) if len(valid_pixels) > 0 else 0

        metadata = {
            'sample_id': sample_idx,
            'width': self.width,
            'height': self.height,
            'min_depth': float(self.min_depth),
            'max_depth': float(self.max_depth),
            'camera_intrinsics': {
                'fx': float(self.fx),
                'fy': float(self.fy),
                'cx': float(self.cx),
                'cy': float(self.cy)
            },
            'depth_statistics': {
                'mean': float(avg_depth),
                'std': float(std_depth),
                'min': float(np.min(valid_pixels)) if len(valid_pixels) > 0 else 0,
                'max': float(np.max(valid_pixels)) if len(valid_pixels) > 0 else 0,
                'valid_pixels': int(np.sum(depth_map > self.min_depth))
            },
            'sensor_type': np.random.choice(['stereo', 'tof', 'structured_light']),
            'noise_model': 'range_dependent',
            'timestamp': sample_idx  # Simplified timestamp
        }

        return metadata

    def convert_to_pointcloud(self, depth_map: np.ndarray) -> np.ndarray:
        """Convert depth map to 3D point cloud"""
        # Create coordinate grids
        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]

        # Convert pixel coordinates to 3D coordinates
        x_3d = (x_coords - self.cx) * depth_map / self.fx
        y_3d = (y_coords - self.cy) * depth_map / self.fy
        z_3d = depth_map

        # Stack into point cloud
        point_cloud = np.stack([x_3d, y_3d, z_3d], axis=-1)

        # Reshape to (N, 3) format
        point_cloud = point_cloud.reshape(-1, 3)

        # Remove invalid points (where depth is max_depth or invalid)
        valid_mask = (z_3d.flatten() < self.max_depth * 0.99) & (z_3d.flatten() > self.min_depth)
        point_cloud = point_cloud[valid_mask]

        return point_cloud

    def run_generation(self):
        """Execute the complete depth generation pipeline"""
        print(f"Generating {self.num_samples} synthetic depth maps...")
        self.generate_depth_maps()

        print(f"Depth generation complete! Output saved to {self.output_dir}")

# Example usage
if __name__ == "__main__":
    depth_gen = DepthGenerator(output_dir="my_depth_dataset", num_samples=500)
    depth_gen.run_generation()
```

## Segmentation Mask Generation

### Semantic and Instance Segmentation

```python
# segmentation_generation.py
import numpy as np
import cv2
from PIL import Image
import json
import os
from typing import Dict, List, Tuple

class SegmentationGenerator:
    def __init__(self, output_dir: str = "synthetic_segmentation_data", num_samples: int = 1000):
        self.output_dir = output_dir
        self.num_samples = num_samples

        # Setup output directories
        self.setup_directories()

        # Define class mapping
        self.class_mapping = {
            0: 'background',
            1: 'robot',
            2: 'cup',
            3: 'book',
            4: 'ball',
            5: 'box',
            6: 'table',
            7: 'chair',
            8: 'person',
            9: 'obstacle'
        }

        # Resolution
        self.width = 640
        self.height = 480

    def setup_directories(self):
        """Create necessary output directories"""
        dirs = [
            f"{self.output_dir}/semantic_masks",
            f"{self.output_dir}/instance_masks",
            f"{self.output_dir}/segmentation_metadata",
            f"{self.output_dir}/panoptic_masks"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def generate_segmentation_masks(self):
        """Generate synthetic segmentation masks"""
        for sample_idx in range(self.num_samples):
            # Create semantic segmentation mask
            semantic_mask = self.create_semantic_mask(sample_idx)

            # Create instance segmentation mask
            instance_mask, instance_info = self.create_instance_mask(semantic_mask, sample_idx)

            # Save masks
            semantic_path = f"{self.output_dir}/semantic_masks/{sample_idx:06d}.png"
            instance_path = f"{self.output_dir}/instance_masks/{sample_idx:06d}.png"

            Image.fromarray(semantic_mask.astype(np.uint8)).save(semantic_path)
            Image.fromarray(instance_mask.astype(np.uint8)).save(instance_path)

            # Save metadata
            metadata = self.generate_segmentation_metadata(sample_idx, semantic_mask, instance_info)
            metadata_path = f"{self.output_dir}/segmentation_metadata/{sample_idx:06d}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            if sample_idx % 100 == 0:
                print(f"Generated {sample_idx + 1}/{self.num_samples} segmentation masks")

    def create_semantic_mask(self, sample_idx: int) -> np.ndarray:
        """Create semantic segmentation mask"""
        semantic_mask = np.zeros((self.height, self.width), dtype=np.uint8)

        # Add different regions for various classes
        center_x, center_y = self.width // 2, self.height // 2

        # Add a central region (e.g., table)
        cv2.circle(semantic_mask, (center_x, center_y), 150, 6, thickness=-1)  # Table

        # Add objects on the table
        num_objects = np.random.randint(3, 6)
        for i in range(num_objects):
            obj_x = np.random.randint(200, self.width - 200)
            obj_y = np.random.randint(150, self.height - 150)
            obj_radius = np.random.randint(20, 50)

            # Assign random object class (excluding background and table)
            obj_class = np.random.choice([2, 3, 4, 5])  # cup, book, ball, box

            cv2.circle(semantic_mask, (obj_x, obj_y), obj_radius, obj_class, thickness=-1)

        # Add some background elements
        # Floor/ground
        cv2.rectangle(semantic_mask, (0, int(0.7 * self.height)), (self.width, self.height), 0, thickness=-1)

        # Add a person in the background
        if np.random.random() < 0.3:  # 30% chance
            person_x = np.random.randint(100, self.width - 100)
            person_y = int(0.8 * self.height)
            cv2.rectangle(semantic_mask,
                         (person_x - 30, person_y - 100),
                         (person_x + 30, person_y),
                         8, thickness=-1)  # Person

        return semantic_mask

    def create_instance_mask(self, semantic_mask: np.ndarray, sample_idx: int) -> Tuple[np.ndarray, List[Dict]]:
        """Create instance segmentation mask from semantic mask"""
        instance_mask = np.zeros_like(semantic_mask)
        instance_info = []

        # For each class, assign unique instance IDs
        for class_id in np.unique(semantic_mask):
            if class_id == 0:  # Skip background
                continue

            # Find all pixels belonging to this class
            class_mask = (semantic_mask == class_id)

            # Find connected components (instances) within this class
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                class_mask.astype(np.uint8), connectivity=8
            )

            # Assign unique instance IDs
            for i in range(1, num_labels):  # Skip background (label 0)
                instance_region = (labels == i)
                instance_id = int(class_id * 1000 + i)  # Combine class and instance
                instance_mask[instance_region] = instance_id

                # Store instance information
                bbox = stats[i][:4]  # x, y, width, height
                area = stats[i][4]

                instance_info.append({
                    'instance_id': instance_id,
                    'class_id': int(class_id),
                    'class_name': self.class_mapping.get(int(class_id), 'unknown'),
                    'bbox': [int(coord) for coord in bbox],
                    'area': int(area),
                    'centroid': [float(centroids[i][0]), float(centroids[i][1])]
                })

        return instance_mask, instance_info

    def generate_segmentation_metadata(self, sample_idx: int, semantic_mask: np.ndarray, instance_info: List[Dict]) -> Dict:
        """Generate metadata for segmentation masks"""
        # Calculate class distribution
        unique, counts = np.unique(semantic_mask, return_counts=True)
        class_distribution = dict(zip(unique, counts))

        # Calculate instance distribution
        instance_classes = [inst['class_id'] for inst in instance_info]
        unique_inst, inst_counts = np.unique(instance_classes, return_counts=True)
        instance_distribution = dict(zip(unique_inst, inst_counts))

        metadata = {
            'sample_id': sample_idx,
            'width': int(self.width),
            'height': int(self.height),
            'semantic_stats': {
                'total_pixels': int(self.width * self.height),
                'class_distribution': {int(k): int(v) for k, v in class_distribution.items()},
                'num_classes': len([k for k in class_distribution.keys() if k != 0])  # Exclude background
            },
            'instance_stats': {
                'total_instances': len(instance_info),
                'instance_distribution': {int(k): int(v) for k, v in instance_distribution.items()},
                'instances': instance_info
            },
            'class_mapping': self.class_mapping,
            'timestamp': sample_idx
        }

        return metadata

    def create_panoptic_segmentation(self, semantic_mask: np.ndarray, instance_mask: np.ndarray) -> np.ndarray:
        """Create panoptic segmentation (combines semantic and instance info)"""
        # Panoptic segmentation typically uses a format where each pixel contains
        # (class_id << 16) + instance_id
        panoptic_mask = semantic_mask.astype(np.int32) << 16
        panoptic_mask = panoptic_mask + instance_mask.astype(np.int32)

        # For stuff classes (non-instance), we use the semantic class id
        # For thing classes (instance), we combine class and instance
        for class_id in np.unique(semantic_mask):
            if class_id in [1, 2, 3, 4, 5, 8]:  # Thing classes (have instances)
                class_instances = (instance_mask > 0) & (semantic_mask == class_id)
                panoptic_mask[class_instances] = (class_id << 16) + instance_mask[class_instances]
            else:  # Stuff classes (no instances)
                class_pixels = semantic_mask == class_id
                panoptic_mask[class_pixels] = class_id << 16

        return panoptic_mask

    def visualize_segmentation(self, rgb_image: np.ndarray, semantic_mask: np.ndarray, instance_mask: np.ndarray) -> np.ndarray:
        """Create visualization of segmentation results"""
        # Create color map for semantic segmentation
        color_map = self.get_color_map()

        # Apply color map to semantic mask
        semantic_vis = color_map[semantic_mask.flatten()].reshape(self.height, self.width, 3)

        # Blend with original image
        alpha = 0.5
        vis_image = (rgb_image * (1 - alpha) + semantic_vis * alpha).astype(np.uint8)

        return vis_image

    def get_color_map(self) -> np.ndarray:
        """Get color map for different classes"""
        # Define colors for each class (in RGB format)
        colors = {
            0: [0, 0, 0],        # background - black
            1: [255, 0, 0],      # robot - red
            2: [0, 255, 0],      # cup - green
            3: [0, 0, 255],      # book - blue
            4: [255, 255, 0],    # ball - yellow
            5: [255, 0, 255],    # box - magenta
            6: [0, 255, 255],    # table - cyan
            7: [128, 128, 128],  # chair - gray
            8: [255, 165, 0],    # person - orange
            9: [128, 0, 128]     # obstacle - purple
        }

        # Create color map array
        max_class_id = max(colors.keys()) + 1
        color_map = np.zeros((max_class_id, 3), dtype=np.uint8)

        for class_id, color in colors.items():
            color_map[class_id] = color

        return color_map

    def run_generation(self):
        """Execute the complete segmentation generation pipeline"""
        print(f"Generating {self.num_samples} synthetic segmentation masks...")
        self.generate_segmentation_masks()

        print(f"Segmentation generation complete! Output saved to {self.output_dir}")

# Example usage
if __name__ == "__main__":
    seg_gen = SegmentationGenerator(output_dir="my_seg_dataset", num_samples=500)
    seg_gen.run_generation()
```

## Domain Randomization

### Enhancing Robustness Through Variation

```python
# domain_randomization.py
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import random
import os

class DomainRandomizer:
    def __init__(self, base_brightness_range=(-0.2, 0.2),
                 base_contrast_range=(0.8, 1.2),
                 base_saturation_range=(0.8, 1.2),
                 base_hue_range=(-0.1, 0.1)):
        self.brightness_range = base_brightness_range
        self.contrast_range = base_contrast_range
        self.saturation_range = base_saturation_range
        self.hue_range = base_hue_range

    def apply_domain_randomization(self, image: np.ndarray,
                                   apply_brightness=True,
                                   apply_contrast=True,
                                   apply_saturation=True,
                                   apply_hue=True,
                                   apply_noise=True,
                                   apply_blur=True) -> np.ndarray:
        """Apply domain randomization to an image"""
        pil_image = Image.fromarray(image)

        # Apply brightness variation
        if apply_brightness:
            brightness_factor = random.uniform(*self.brightness_range) + 1.0
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(brightness_factor)

        # Apply contrast variation
        if apply_contrast:
            contrast_factor = random.uniform(*self.contrast_range)
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(contrast_factor)

        # Apply saturation variation
        if apply_saturation:
            saturation_factor = random.uniform(*self.saturation_range)
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhander.enhance(saturation_factor)

        # Apply hue variation (as PIL doesn't have direct hue adjustment, we'll use a workaround)
        if apply_hue:
            pil_image = self.apply_hue_shift(pil_image, random.uniform(*self.hue_range))

        # Apply noise
        if apply_noise:
            pil_image = self.add_random_noise(np.array(pil_image))
            pil_image = Image.fromarray(pil_image)

        # Apply blur
        if apply_blur:
            blur_amount = random.uniform(0, 1.5)
            if blur_amount > 0.1:
                pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=blur_amount))

        return np.array(pil_image)

    def apply_hue_shift(self, image: Image.Image, hue_shift: float) -> Image.Image:
        """Apply hue shift to image"""
        # Convert to HSV, shift hue, convert back to RGB
        hsv = np.array(image.convert('HSV')).astype(np.float32)

        # Shift hue channel
        hsv[:, :, 0] = (hsv[:, :, 0] / 255.0 + hue_shift) % 1.0
        hsv[:, :, 0] = hsv[:, :, 0] * 255.0

        # Convert back to RGB
        rgb = Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')
        return rgb

    def add_random_noise(self, image: np.ndarray) -> np.ndarray:
        """Add random noise to image"""
        # Add different types of noise
        noise_type = random.choice(['gaussian', 'poisson', 'salt_pepper'])

        if noise_type == 'gaussian':
            mean = 0
            sigma = random.uniform(5, 15)
            gauss = np.random.normal(mean, sigma, image.shape).astype(np.float32)
            noisy_image = image.astype(np.float32) + gauss
            return np.clip(noisy_image, 0, 255).astype(np.uint8)

        elif noise_type == 'poisson':
            # Poisson noise (more realistic for photon noise)
            noisy_image = np.random.poisson(image.astype(np.float32))
            return np.clip(noisy_image, 0, 255).astype(np.uint8)

        elif noise_type == 'salt_pepper':
            # Salt and pepper noise
            prob = random.uniform(0.001, 0.01)
            noisy_image = image.copy()

            # Salt
            salt = np.random.random(image.shape[:2]) < prob / 2
            noisy_image[salt] = 255

            # Pepper
            pepper = np.random.random(image.shape[:2]) < prob / 2
            noisy_image[pepper] = 0

            return noisy_image

        return image

    def randomize_lighting_conditions(self) -> Dict:
        """Generate random lighting conditions"""
        lighting_conditions = {
            'intensity': random.uniform(0.5, 2.0),  # 0.5x to 2x normal
            'temperature': random.uniform(3000, 8000),  # Color temperature in Kelvin
            'directional_light_ratio': random.uniform(0.2, 0.8),
            'ambient_light_ratio': random.uniform(0.2, 0.6),
            'shadows_enabled': random.choice([True, False]),
            'specular_highlight': random.uniform(0.1, 1.0)
        }
        return lighting_conditions

    def randomize_material_properties(self) -> Dict:
        """Generate random material properties"""
        material_properties = {
            'roughness': random.uniform(0.05, 0.95),
            'metallic': random.uniform(0.0, 0.8),
            'specular': random.uniform(0.1, 1.0),
            'subsurface': random.uniform(0.0, 0.1),
            'anisotropic': random.uniform(0.0, 0.2),
            'sheen': random.uniform(0.0, 1.0),
            'clearcoat': random.uniform(0.0, 1.0),
            'opacity': random.uniform(0.8, 1.0)
        }
        return material_properties

    def randomize_camera_parameters(self) -> Dict:
        """Generate random camera parameters"""
        camera_params = {
            'exposure': random.uniform(0.1, 2.0),
            'iso': random.randint(100, 1600),
            'aperture': random.uniform(1.4, 16.0),
            'shutter_speed': random.uniform(1/8000, 1/30),  # In seconds
            'white_balance': random.uniform(-0.1, 0.1),  # Color temperature adjustment
            'sharpness': random.uniform(0.5, 2.0),
            'vignetting': random.uniform(0.0, 0.3)
        }
        return camera_params

    def apply_environmental_effects(self, image: np.ndarray) -> np.ndarray:
        """Apply environmental effects like fog, rain, etc."""
        effect_type = random.choice(['none', 'fog', 'rain', 'snow', 'dust'])

        if effect_type == 'fog':
            return self.add_fog_effect(image)
        elif effect_type == 'rain':
            return self.add_rain_effect(image)
        elif effect_type == 'snow':
            return self.add_snow_effect(image)
        elif effect_type == 'dust':
            return self.add_dust_effect(image)
        else:
            return image

    def add_fog_effect(self, image: np.ndarray) -> np.ndarray:
        """Add fog effect to image"""
        fog_density = random.uniform(0.05, 0.3)

        # Create depth-based fog (simulate distance fog)
        height, width = image.shape[:2]
        # Assume center is closer, edges are farther (simplified)
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        x_grid, y_grid = np.meshgrid(x, y)
        distance = np.sqrt(x_grid**2 + y_grid**2)

        fog_mask = distance * fog_density
        fog_mask = np.clip(fog_mask, 0, 1)

        # Apply fog (blend with white)
        fog_color = np.array([248, 248, 255])  # Light grayish white
        fogged_image = image * (1 - fog_mask[..., np.newaxis]) + fog_color * fog_mask[..., np.newaxis]

        return np.clip(fogged_image, 0, 255).astype(np.uint8)

    def add_rain_effect(self, image: np.ndarray) -> np.ndarray:
        """Add rain effect to image"""
        rain_density = random.uniform(0.1, 0.5)

        # Create rain streaks
        height, width = image.shape[:2]
        rain_layer = np.zeros((height, width, 3), dtype=np.uint8)

        # Add diagonal rain streaks
        num_streaks = int(width * rain_density)
        for _ in range(num_streaks):
            x_start = random.randint(0, width)
            y_start = random.randint(0, height // 2)

            length = random.randint(10, 50)
            thickness = random.randint(1, 3)

            points = []
            for i in range(length):
                x = x_start + i
                y = y_start + i * 2  # Diagonal
                if 0 <= x < width and 0 <= y < height:
                    points.append((x, y))

            for x, y in points:
                if 0 <= x < width and 0 <= y < height:
                    rain_layer[y, x] = [200, 200, 220]  # Light gray rain streaks

        # Blend rain with original image
        rain_opacity = random.uniform(0.1, 0.3)
        result = image * (1 - rain_opacity) + rain_layer * rain_opacity

        return np.clip(result, 0, 255).astype(np.uint8)

    def add_snow_effect(self, image: np.ndarray) -> np.ndarray:
        """Add snow effect to image"""
        snow_density = random.uniform(0.01, 0.1)

        height, width = image.shape[:2]

        # Create snowflakes
        snow_mask = np.random.random((height, width)) < snow_density

        # Make snowflakes brighter
        snow_layer = np.zeros_like(image)
        snow_layer[snow_mask] = [255, 255, 250]  # Almost white snow

        # Add some sparkle effect
        sparkle_mask = snow_mask & (np.random.random((height, width)) < 0.1)
        snow_layer[sparkle_mask] = [255, 255, 255]  # Pure white sparkles

        # Blend with original
        snow_opacity = random.uniform(0.1, 0.4)
        result = image * (1 - snow_opacity) + snow_layer * snow_opacity

        return np.clip(result, 0, 255).astype(np.uint8)

    def add_dust_effect(self, image: np.ndarray) -> np.ndarray:
        """Add dust/smoke effect to image"""
        dust_density = random.uniform(0.005, 0.05)

        height, width = image.shape[:2]

        # Create dust particles
        dust_mask = np.random.random((height, width)) < dust_density

        # Dust color (brownish-gray)
        dust_color = np.array([180, 160, 140])

        dust_layer = np.zeros_like(image)
        dust_layer[dust_mask] = dust_color

        # Add some variation in dust size and opacity
        for _ in range(random.randint(10, 50)):
            cx = random.randint(0, width)
            cy = random.randint(0, height)
            radius = random.randint(1, 5)

            y, x = np.ogrid[:height, :width]
            mask = (x - cx)**2 + (y - cy)**2 <= radius**2
            dust_layer[mask] = dust_color

        # Blend with original
        dust_opacity = random.uniform(0.05, 0.2)
        result = image * (1 - dust_opacity) + dust_layer * dust_opacity

        return np.clip(result, 0, 255).astype(np.uint8)

# Integration example with the generators
def integrate_domain_randomization():
    """Show how to integrate domain randomization with generators"""

    # Initialize domain randomizer
    randomizer = DomainRandomizer()

    # Example: Apply to RGB images during generation
    def apply_randomization_to_image(image, sample_idx):
        # Apply domain randomization
        randomized_image = randomizer.apply_domain_randomization(
            image,
            apply_brightness=True,
            apply_contrast=True,
            apply_saturation=True,
            apply_hue=random.choice([True, False]),  # Sometimes skip hue for variety
            apply_noise=True,
            apply_blur=random.choice([True, False])  # Sometimes skip blur
        )

        # Apply environmental effects
        if random.random() < 0.3:  # 30% chance of environmental effects
            randomized_image = randomizer.apply_environmental_effects(randomized_image)

        return randomized_image

    # Example lighting and material randomization for 3D scenes
    def get_random_scene_parameters(sample_idx):
        lighting = randomizer.randomize_lighting_conditions()
        materials = randomizer.randomize_material_properties()
        camera = randomizer.randomize_camera_parameters()

        return {
            'lighting': lighting,
            'materials': materials,
            'camera': camera,
            'sample_id': sample_idx
        }

    print("Domain randomization integration ready!")
    return apply_randomization_to_image, get_random_scene_parameters

if __name__ == "__main__":
    # Demonstrate domain randomization
    randomizer = DomainRandomizer()

    # Create a sample image to test
    sample_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Apply domain randomization
    randomized = randomizer.apply_domain_randomization(sample_image)

    print("Domain randomization test completed!")
```

## Data Validation and Quality Assessment

### Ensuring High-Quality Synthetic Data

```python
# data_validation.py
import numpy as np
import cv2
from PIL import Image
import json
import os
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class DataQualityValidator:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.results = {}

    def validate_rgb_quality(self, sample_count: int = 100) -> Dict:
        """Validate RGB image quality"""
        image_dir = os.path.join(self.dataset_path, 'images')
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

        # Sample images for validation
        sampled_files = np.random.choice(image_files, min(sample_count, len(image_files)), replace=False)

        quality_metrics = {
            'sharpness': [],
            'brightness': [],
            'contrast': [],
            'saturation': [],
            'color_balance': [],
            'noise_level': []
        }

        for img_file in sampled_files:
            img_path = os.path.join(image_dir, img_file)
            img = cv2.imread(img_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Sharpness (using Laplacian variance)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'].append(float(laplacian_var))

            # Brightness (mean of HSV value channel)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            brightness = np.mean(hsv[:, :, 2])
            quality_metrics['brightness'].append(float(brightness))

            # Contrast (standard deviation of luminance)
            lum = np.dot(img_rgb[...,:3], [0.299, 0.587, 0.114])
            contrast = np.std(lum)
            quality_metrics['contrast'].append(float(contrast))

            # Saturation (mean of HSV saturation channel)
            saturation = np.mean(hsv[:, :, 1])
            quality_metrics['saturation'].append(float(saturation))

            # Color balance (ratios of color channels)
            mean_rgb = np.mean(img_rgb, axis=(0, 1))
            color_balance = float(mean_rgb[0] / (mean_rgb[2] + 1e-6))  # R/B ratio
            quality_metrics['color_balance'].append(color_balance)

            # Noise level (difference between original and smoothed)
            smoothed = cv2.GaussianBlur(img, (5, 5), 0)
            noise = np.mean(np.abs(img.astype(np.float32) - smoothed.astype(np.float32)))
            quality_metrics['noise_level'].append(float(noise))

        # Calculate statistics
        validation_results = {}
        for metric, values in quality_metrics.items():
            if values:
                validation_results[metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }

        return validation_results

    def validate_depth_quality(self, sample_count: int = 100) -> Dict:
        """Validate depth map quality"""
        depth_dir = os.path.join(self.dataset_path, 'depth_maps')
        depth_files = [f for f in os.listdir(depth_dir) if f.endswith(('.png', '.exr', '.tiff'))]

        sampled_files = np.random.choice(depth_files, min(sample_count, len(depth_files)), replace=False)

        depth_metrics = {
            'valid_pixel_ratio': [],
            'mean_depth': [],
            'depth_range': [],
            'discontinuity_ratio': [],
            'smoothness': []
        }

        for depth_file in sampled_files:
            depth_path = os.path.join(depth_dir, depth_file)

            # Load depth map (assuming it's saved as 16-bit PNG with scaling)
            depth_img = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

            # Convert back to actual depth values
            min_depth = 0.1  # meters
            max_depth = 10.0  # meters
            actual_depth = (depth_img.astype(np.float32) / 65535.0) * (max_depth - min_depth) + min_depth

            # Calculate metrics
            valid_mask = (actual_depth > min_depth) & (actual_depth < max_depth * 0.99)
            valid_pixel_ratio = np.sum(valid_mask) / actual_depth.size
            depth_metrics['valid_pixel_ratio'].append(float(valid_pixel_ratio))

            mean_depth = np.mean(actual_depth[valid_mask]) if np.any(valid_mask) else 0
            depth_metrics['mean_depth'].append(float(mean_depth))

            depth_range = np.ptp(actual_depth[valid_mask]) if np.any(valid_mask) else 0
            depth_metrics['depth_range'].append(float(depth_range))

            # Discontinuity (edge detection in depth map)
            grad_x = np.gradient(actual_depth, axis=1)
            grad_y = np.gradient(actual_depth, axis=0)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            discontinuity_ratio = np.sum(gradient_magnitude > 0.1) / gradient_magnitude.size
            depth_metrics['discontinuity_ratio'].append(float(discontinuity_ratio))

            # Smoothness (inverse of gradient magnitude)
            smoothness = 1.0 / (1.0 + np.mean(gradient_magnitude))
            depth_metrics['smoothness'].append(float(smoothness))

        # Calculate statistics
        validation_results = {}
        for metric, values in depth_metrics.items():
            if values:
                validation_results[metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }

        return validation_results

    def validate_segmentation_quality(self, sample_count: int = 100) -> Dict:
        """Validate segmentation mask quality"""
        semantic_dir = os.path.join(self.dataset_path, 'semantic_masks')
        instance_dir = os.path.join(self.dataset_path, 'instance_masks')

        semantic_files = [f for f in os.listdir(semantic_dir) if f.endswith('.png')]
        instance_files = [f for f in os.listdir(instance_dir) if f.endswith('.png')]

        sampled_files = np.random.choice(semantic_files, min(sample_count, len(semantic_files)), replace=False)

        seg_metrics = {
            'class_diversity': [],
            'instance_diversity': [],
            'coverage_ratio': [],
            'object_size_variety': []
        }

        for seg_file in sampled_files:
            # Load semantic mask
            sem_path = os.path.join(semantic_dir, seg_file)
            sem_mask = np.array(Image.open(sem_path))

            # Load instance mask
            inst_path = os.path.join(instance_dir, seg_file)  # Assuming same filenames
            if os.path.exists(inst_path):
                inst_mask = np.array(Image.open(inst_path))
            else:
                inst_mask = np.zeros_like(sem_mask)  # Default if instance mask doesn't exist

            # Calculate metrics
            unique_classes = len(np.unique(sem_mask))
            seg_metrics['class_diversity'].append(float(unique_classes))

            unique_instances = len(np.unique(inst_mask))
            seg_metrics['instance_diversity'].append(float(unique_instances))

            coverage_ratio = np.sum(sem_mask != 0) / sem_mask.size
            seg_metrics['coverage_ratio'].append(float(coverage_ratio))

            # Object size variety (coefficient of variation of object sizes)
            if len(np.unique(sem_mask)) > 1:  # More than just background
                object_sizes = []
                for class_id in np.unique(sem_mask):
                    if class_id != 0:  # Skip background
                        size = np.sum(sem_mask == class_id)
                        object_sizes.append(size)

                if object_sizes and len(object_sizes) > 1:
                    sizes_array = np.array(object_sizes)
                    cv = np.std(sizes_array) / np.mean(sizes_array) if np.mean(sizes_array) != 0 else 0
                    seg_metrics['object_size_variety'].append(float(cv))
                else:
                    seg_metrics['object_size_variety'].append(0.0)
            else:
                seg_metrics['object_size_variety'].append(0.0)

        # Calculate statistics
        validation_results = {}
        for metric, values in seg_metrics.items():
            if values:
                validation_results[metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }

        return validation_results

    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality report"""
        print("Validating RGB quality...")
        rgb_metrics = self.validate_rgb_quality()

        print("Validating depth quality...")
        depth_metrics = self.validate_depth_quality()

        print("Validating segmentation quality...")
        seg_metrics = self.validate_segmentation_quality()

        report = {
            'dataset_path': self.dataset_path,
            'validation_timestamp': np.datetime64('now').astype(str),
            'rgb_quality': rgb_metrics,
            'depth_quality': depth_metrics,
            'segmentation_quality': seg_metrics,
            'overall_assessment': self.assess_dataset_quality(rgb_metrics, depth_metrics, seg_metrics)
        }

        # Save report
        report_path = os.path.join(self.dataset_path, 'quality_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def assess_dataset_quality(self, rgb_metrics: Dict, depth_metrics: Dict, seg_metrics: Dict) -> Dict:
        """Assess overall dataset quality"""
        assessment = {
            'rgb_score': self.calculate_rgb_score(rgb_metrics),
            'depth_score': self.calculate_depth_score(depth_metrics),
            'segmentation_score': self.calculate_segmentation_score(seg_metrics),
            'recommendations': []
        }

        # Calculate overall score
        overall_score = (
            assessment['rgb_score'] * 0.4 +
            assessment['depth_score'] * 0.3 +
            assessment['segmentation_score'] * 0.3
        )

        assessment['overall_score'] = overall_score

        # Generate recommendations based on metrics
        if rgb_metrics.get('sharpness', {}).get('mean', 0) < 100:
            assessment['recommendations'].append("Images appear blurry - consider increasing sharpness in rendering pipeline")

        if depth_metrics.get('valid_pixel_ratio', {}).get('mean', 0) < 0.8:
            assessment['recommendations'].append("Low valid pixel ratio in depth maps - check for proper depth rendering")

        if seg_metrics.get('class_diversity', {}).get('mean', 0) < 3:
            assessment['recommendations'].append("Limited class diversity in segmentation - add more object types")

        return assessment

    def calculate_rgb_score(self, metrics: Dict) -> float:
        """Calculate RGB quality score (0-1 scale)"""
        score = 0.0

        # Sharpness contributes 30%
        sharpness_mean = metrics.get('sharpness', {}).get('mean', 0)
        score += min(1.0, sharpness_mean / 500) * 0.3  # Assume 500 is excellent sharpness

        # Contrast contributes 25%
        contrast_mean = metrics.get('contrast', {}).get('mean', 0)
        score += min(1.0, contrast_mean / 50) * 0.25  # Assume 50 is excellent contrast

        # Valid range contributes 20%
        brightness_mean = metrics.get('brightness', {}).get('mean', 0)
        if 50 <= brightness_mean <= 200:  # Good brightness range
            score += 0.2
        elif 20 <= brightness_mean <= 235:  # Acceptable range
            score += 0.1

        # Color balance contributes 25%
        color_balance = metrics.get('color_balance', {}).get('mean', 1.0)
        if 0.5 <= color_balance <= 2.0:  # Reasonable R/B balance
            score += 0.25

        return min(1.0, score)

    def calculate_depth_score(self, metrics: Dict) -> float:
        """Calculate depth quality score (0-1 scale)"""
        score = 0.0

        # Valid pixel ratio contributes 40%
        valid_ratio = metrics.get('valid_pixel_ratio', {}).get('mean', 0)
        score += valid_ratio * 0.4

        # Depth range contributes 30%
        depth_range = metrics.get('depth_range', {}).get('mean', 0)
        if depth_range > 1.0:  # Good depth variation
            score += 0.3

        # Smoothness contributes 30%
        smoothness = metrics.get('smoothness', {}).get('mean', 0)
        if smoothness > 0.5:  # Reasonably smooth
            score += min(0.3, smoothness * 0.3)

        return min(1.0, score)

    def calculate_segmentation_score(self, metrics: Dict) -> float:
        """Calculate segmentation quality score (0-1 scale)"""
        score = 0.0

        # Class diversity contributes 40%
        class_div = metrics.get('class_diversity', {}).get('mean', 0)
        score += min(1.0, class_div / 10) * 0.4  # Assume 10+ classes is excellent

        # Coverage ratio contributes 30%
        coverage = metrics.get('coverage_ratio', {}).get('mean', 0)
        score += coverage * 0.3

        # Instance diversity contributes 30%
        inst_div = metrics.get('instance_diversity', {}).get('mean', 0)
        score += min(1.0, inst_div / 20) * 0.3  # Assume 20+ instances is excellent

        return min(1.0, score)

    def visualize_quality_metrics(self, report: Dict):
        """Create visualizations of quality metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # RGB metrics
        rgb_means = [report['rgb_quality'][k]['mean'] for k in report['rgb_quality'].keys()]
        rgb_names = list(report['rgb_quality'].keys())

        axes[0, 0].bar(rgb_names, rgb_means)
        axes[0, 0].set_title('RGB Quality Metrics')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # Depth metrics
        depth_means = [report['depth_quality'][k]['mean'] for k in report['depth_quality'].keys()]
        depth_names = list(report['depth_quality'].keys())

        axes[0, 1].bar(depth_names, depth_means)
        axes[0, 1].set_title('Depth Quality Metrics')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # Segmentation metrics
        seg_means = [report['segmentation_quality'][k]['mean'] for k in report['segmentation_quality'].keys()]
        seg_names = list(report['segmentation_quality'].keys())

        axes[1, 0].bar(seg_names, seg_means)
        axes[1, 0].set_title('Segmentation Quality Metrics')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # Quality scores
        scores = [
            report['overall_assessment']['rgb_score'],
            report['overall_assessment']['depth_score'],
            report['overall_assessment']['segmentation_score'],
            report['overall_assessment']['overall_score']
        ]
        score_names = ['RGB Score', 'Depth Score', 'Seg Score', 'Overall Score']

        bars = axes[1, 1].bar(score_names, scores, color=['blue', 'green', 'orange', 'red'])
        axes[1, 1].set_title('Quality Scores')
        axes[1, 1].set_ylim(0, 1)

        # Add value labels on bars
        for bar, score in zip(bars, scores):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                            f'{score:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(os.path.join(self.dataset_path, 'quality_visualization.png'), dpi=300, bbox_inches='tight')
        plt.show()

# Example usage
if __name__ == "__main__":
    # Example of how to use the validator
    validator = DataQualityValidator("my_synthetic_dataset")
    report = validator.generate_quality_report()
    validator.visualize_quality_metrics(report)

    print(f"Dataset quality score: {report['overall_assessment']['overall_score']:.2f}")
    print(f"Recommendations: {report['overall_assessment']['recommendations']}")
```

This comprehensive guide covers the generation of RGB, depth, and segmentation data for synthetic data generation, providing the foundation for training robust perception systems in humanoid robots with vision-language-action capabilities.