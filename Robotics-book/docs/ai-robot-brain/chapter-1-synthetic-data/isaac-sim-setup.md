---
sidebar_position: 2
---

# Isaac Sim Setup and Configuration

## Installing and Configuring NVIDIA Isaac Sim for Synthetic Data Generation

NVIDIA Isaac Sim is a powerful simulation environment for robotics that enables high-fidelity synthetic data generation. This chapter covers the installation, configuration, and optimization of Isaac Sim for creating training data for humanoid robot perception systems.

## Learning Objectives

By the end of this chapter, you will:
- Install and configure NVIDIA Isaac Sim
- Set up the development environment for synthetic data generation
- Configure GPU acceleration and rendering settings
- Optimize performance for data generation workflows
- Integrate Isaac Sim with ROS 2 and other robotics frameworks

## System Requirements

### Hardware Requirements
- **GPU**: NVIDIA RTX series (RTX 3060 or higher recommended)
- **VRAM**: 8GB minimum, 16GB+ recommended for high-fidelity rendering
- **CPU**: Multi-core processor (Intel i7 or AMD Ryzen 7+)
- **RAM**: 16GB minimum, 32GB+ recommended
- **Storage**: SSD with 100GB+ free space for assets and datasets
- **OS**: Ubuntu 20.04/22.04 LTS or Windows 10/11

### Software Requirements
- **CUDA**: 11.8 or higher
- **Driver**: NVIDIA driver 520+ (Linux) or 531+ (Windows)
- **Python**: 3.8-3.10
- **Docker**: For containerized deployments
- **ROS 2**: Humble Hawksbill or newer

## Isaac Sim Installation

### Method 1: Omniverse Launcher (Recommended)

1. **Download Omniverse Launcher**:
   - Visit [developer.nvidia.com/omniverse](https://developer.nvidia.com/omniverse)
   - Download and install the Omniverse Launcher
   - Sign in with your NVIDIA Developer account

2. **Install Isaac Sim**:
   ```bash
   # Launch Omniverse Launcher
   ./OmniverseLauncher.AppImage  # Linux
   # or run Omniverse Launcher.exe on Windows

   # In the launcher, search for "Isaac Sim"
   # Click "Install" to download and install
   ```

3. **Verify Installation**:
   ```bash
   # Check Isaac Sim version
   python -c "import omni; print('Isaac Sim installed successfully')"
   ```

### Method 2: Docker Container (Alternative)

```bash
# Pull Isaac Sim Docker image
docker pull nvcr.io/nvidia/isaac-sim:4.0.0

# Run Isaac Sim container
docker run --gpus all -it --rm \
  --network=host \
  --env "DISPLAY" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --volume="${PWD}:/workspace" \
  --workdir="/workspace" \
  nvcr.io/nvidia/isaac-sim:4.0.0
```

### Method 3: Source Installation (Advanced)

```bash
# Clone Isaac Sim repository
git clone https://github.com/NVIDIA-Omniverse/Isaac-Sim.git
cd Isaac-Sim

# Install dependencies
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Create virtual environment
python3.10 -m venv isaac-sim-env
source isaac-sim-env/bin/activate

# Install Isaac Sim
pip install -e .
```

## Initial Configuration

### Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export ISAACSIM_PATH="/path/to/isaac-sim"
export PYTHONPATH="${ISAACSIM_PATH}/python:${PYTHONPATH}"
export OMNI_DATA_PATH="${HOME}/omniverse/data"
export CUDA_DEVICE_ORDER="PCI_BUS_ID"
export CUDA_VISIBLE_DEVICES="0"  # Use first GPU

# GPU settings
export NV_GPU_FORCE_COMPUTE_PREEMPTION=1
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
```

### Isaac Sim Configuration File

Create a configuration file for synthetic data generation:

```bash
# Create config directory
mkdir -p ~/.config/Isaac-Sim/

# Create configuration file
cat > ~/.config/Isaac-Sim/config.yaml << EOF
settings:
  app:
    window_width: 1920
    window_height: 1080
    enable_viewport_dpi_scale: true
    enable_viewport_render_updates: true
    show_developer_menu: true

  physics:
    solver_type: 0  # 0=PGS, 1=TGS
    solver_position_iteration_count: 8
    solver_velocity_iteration_count: 1
    gpu_max_particles: 1000000
    gpu_heap_size: 67108864  # 64MB

  rendering:
    render_frame_limit: 0  # Unlimited for batch processing
    max_gpu_cache_size: 1073741824  # 1GB
    max_cpu_cache_size: 1073741824  # 1GB
    enable_ground_plane: false
    enable_shadow_cache: true
    enable_texture_cache: true

  camera:
    enable_cpp_extensions: true
    enable_cuda_interop: true
    default_resolution:
      width: 640
      height: 480
    default_fov: 60.0

  synthetic_data:
    enable_semantic_segmentation: true
    enable_instance_segmentation: true
    enable_depth_map: true
    enable_bounding_box_2d_tight: true
    enable_bounding_box_2d_loose: true
    enable_bounding_box_3d: true
    enable_normal_buffer: true
    enable_motion_vector: true

  performance:
    enable_parallel_scene_updates: true
    enable_gpu_physics: true
    gpu_max_particle_contacts: 100000
    gpu_max_contact_pairs: 1000000
    gpu_max_triangles: 5000000
    gpu_max_vertices: 2000000

extensions:
  enabled:
    - omni.isaac.synthetic_utils
    - omni.isaac.range_sensor
    - omni.isaac.ros2_bridge
    - omni.isaac.sensor
    - omni.kit.primitive.mesh
    - omni.kit.material.library
    - omni.kit.viewport.utility
  disabled: []
EOF
```

## GPU and Rendering Optimization

### NVIDIA GPU Configuration

```bash
# Check GPU status
nvidia-smi

# Verify CUDA installation
nvcc --version
nvidia-ml-py3 --version

# Test GPU acceleration
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device count: {torch.cuda.device_count()}')"
```

### Isaac Sim GPU Settings

```python
# gpu_optimization.py
import carb
import omni
from omni.isaac.core import World
from omni.isaac.core.utils import stage
from omni.isaac.synthetic_utils import SyntheticDataHelper

def configure_gpu_settings():
    """Configure GPU settings for optimal synthetic data generation"""

    # Enable GPU physics
    carb.settings.get_settings().set("/physics/solverType", 1)  # TGS solver
    carb.settings.get_settings().set("/physics/gpuSimulation", True)
    carb.settings.get_settings().set("/physics/gpuMaxParticles", 1000000)
    carb.settings.get_settings().set("/physics/gpuHeapSize", 67108864)  # 64MB

    # Rendering optimizations
    carb.settings.get_settings().set("/rtx/scene/maxRayLength", 1000.0)
    carb.settings.get_settings().set("/rtx/indirectDiffuse/enable", False)
    carb.settings.get_settings().set("/rtx/denoise/enable", False)  # Disable denoising for speed
    carb.settings.get_settings().set("/rtx/pathTracing/enable", False)  # Use rasterization
    carb.settings.get_settings().set("/renderer/maxCacheSize", 1073741824)  # 1GB

    # Synthetic data optimizations
    carb.settings.get_settings().set("/app/window/drawMouse", False)
    carb.settings.get_settings().set("/app/renderer/enableViewportUpdates", False)
    carb.settings.get_settings().set("/app/rendering/frameLimit", 0)  # Unlimited for batch

def setup_rendering_pipeline():
    """Setup optimized rendering pipeline for synthetic data"""

    # Configure viewport settings
    viewport_window = omni.ui.Workspace.get_window("Viewport")
    if viewport_window:
        # Set viewport to maximum performance mode
        carb.settings.get_settings().set("/app/viewer/maxFps", 0)  # Unlimited FPS
        carb.settings.get_settings().set("/app/viewer/updateTargetFps", 0)  # No target FPS

def enable_batch_rendering():
    """Configure settings for batch rendering operations"""

    # Disable UI updates during batch processing
    carb.settings.get_settings().set("/app/showViewports", False)
    carb.settings.get_settings().set("/app/showStatusBar", False)
    carb.settings.get_settings().set("/app/showMenuBar", False)
    carb.settings.get_settings().set("/app/window/drawMouse", False)

    # Optimize for CPU utilization during rendering
    carb.settings.get_settings().set("/app/runLoops/update/renderingUpdate/catchUpToSimulation", False)

# Example usage
if __name__ == "__main__":
    configure_gpu_settings()
    setup_rendering_pipeline()
    enable_batch_rendering()

    print("GPU and rendering optimizations applied successfully")
```

## Synthetic Data Extension Configuration

### Enable Synthetic Data Extensions

```python
# synthetic_data_setup.py
import omni
from omni.isaac.synthetic_utils import SyntheticDataHelper
from omni.isaac.core import World
import carb

class SyntheticDataConfigurator:
    def __init__(self):
        self.sd_helper = None

    def enable_synthetic_data_streams(self):
        """Enable required synthetic data streams for training"""

        # Enable all required synthetic data streams
        synth_keys = [
            "rgb",                    # Color images
            "semantic",               # Semantic segmentation
            "instance",               # Instance segmentation
            "depthLinear",            # Depth maps
            "boundingBox2DTight",     # 2D bounding boxes
            "boundingBox2DLoose",     # Loose 2D bounding boxes
            "boundingBox3D",          # 3D bounding boxes
            "normal",                 # Surface normals
            "motionVector",           # Motion vectors
            "camera",                 # Camera info
        ]

        # Configure synthetic data helper
        self.sd_helper = SyntheticDataHelper(attach_viewport=True)

        # Enable specific streams
        for key in synth_keys:
            try:
                self.sd_helper._enable_imaging_sensor(key)
                print(f"Enabled synthetic data stream: {key}")
            except Exception as e:
                print(f"Failed to enable {key}: {e}")

    def configure_camera_settings(self):
        """Configure camera for optimal synthetic data capture"""

        # Set camera resolution
        carb.settings.get_settings().set("/camera/defaultResolution/width", 640)
        carb.settings.get_settings().set("/camera/defaultResolution/height", 480)
        carb.settings.get_settings().set("/camera/defaultFov", 60.0)  # 60 degrees

        # Configure for synthetic data
        carb.settings.get_settings().set("/camera/enableCppExtensions", True)
        carb.settings.get_settings().set("/camera/enableCudaInterop", True)

    def setup_annotation_formats(self):
        """Setup annotation formats for different ML frameworks"""

        # Configure semantic segmentation
        carb.settings.get_settings().set("/semantics/enable", True)
        carb.settings.get_settings().set("/semantics/defaultMaterial", "Material")

        # Configure instance segmentation
        carb.settings.get_settings().set("/instance/enable", True)
        carb.settings.get_settings().set("/instance/idAssignment", "auto")

        # Configure bounding boxes
        carb.settings.get_settings().set("/bbox/enable", True)
        carb.settings.get_settings().set("/bbox/format", "coco")  # COCO format

def initialize_synthetic_data_system():
    """Initialize the complete synthetic data generation system"""

    # Configure Isaac Sim for synthetic data
    config = SyntheticDataConfigurator()
    config.enable_synthetic_data_streams()
    config.configure_camera_settings()
    config.setup_annotation_formats()

    print("Synthetic data system initialized successfully")

    # Verify configuration
    verify_configuration()

def verify_configuration():
    """Verify that synthetic data system is properly configured"""

    # Check if synthetic data extensions are available
    extensions = omni.kit.app.get_app().get_extension_registry().get_extensions()
    synthetic_exts = [ext for ext in extensions if "synthetic" in ext["name"].lower()]

    if synthetic_exts:
        print(f"Found {len(synthetic_exts)} synthetic data extensions:")
        for ext in synthetic_exts:
            print(f"  - {ext['name']}")
    else:
        print("Warning: No synthetic data extensions found")

    # Check GPU availability
    import torch
    if torch.cuda.is_available():
        print(f"CUDA available: {torch.cuda.get_device_name()}")
    else:
        print("Warning: CUDA not available - synthetic data generation may be slow")

if __name__ == "__main__":
    initialize_synthetic_data_system()
```

## Performance Optimization

### Batch Processing Configuration

```python
# batch_processing_config.py
import carb
import omni
from omni.isaac.core import World
import gc

class BatchProcessingOptimizer:
    def __init__(self):
        self.batch_size = 32
        self.memory_limit = 8 * 1024 * 1024 * 1024  # 8GB limit
        self.processed_samples = 0

    def configure_batch_settings(self):
        """Configure settings for efficient batch processing"""

        # Disable unnecessary updates during batch
        carb.settings.get_settings().set("/app/runLoops/update/physicsUpdate/enable", True)
        carb.settings.get_settings().set("/app/runLoops/update/renderingUpdate/enable", True)
        carb.settings.get_settings().set("/app/runLoops/update/sceneUpdate/enable", True)

        # Memory management
        carb.settings.get_settings().set("/app/memory/lowMemoryMode", False)
        carb.settings.get_settings().set("/renderer/maxCacheSize", 2147483648)  # 2GB
        carb.settings.get_settings().set("/app/memory/maxCacheSize", 2147483648)  # 2GB

        # Disable anti-aliasing for speed
        carb.settings.get_settings().set("/rtx/antialiasing/enable", False)
        carb.settings.get_settings().set("/rtx/dlss/enable", False)

        # Optimize for CPU-GPU pipeline
        carb.settings.get_settings().set("/app/runLoops/update/renderingUpdate/catchUpToSimulation", False)
        carb.settings.get_settings().set("/app/runLoops/update/physicsUpdate/catchUpToSimulation", False)

    def setup_memory_management(self):
        """Setup memory management for large-scale data generation"""

        # Configure garbage collection
        gc.enable()
        gc.set_threshold(700, 10, 10)  # Adjust GC frequency

        # Memory monitoring
        import psutil
        self.initial_memory = psutil.virtual_memory().used

    def optimize_for_throughput(self):
        """Optimize settings for maximum data generation throughput"""

        # Increase physics substeps for stability while maintaining speed
        carb.settings.get_settings().set("/physics/solverPositionIterationCount", 4)
        carb.settings.get_settings().set("/physics/solverVelocityIterationCount", 1)

        # Optimize rendering pipeline
        carb.settings.get_settings().set("/renderer/resolution/width", 640)
        carb.settings.get_settings().set("/renderer/resolution/height", 480)
        carb.settings.get_settings().set("/renderer/resolution/pixelsPerUnit", 100)

        # Disable expensive rendering features
        carb.settings.get_settings().set("/rtx/lighting/shadows/enable", True)  # Keep shadows for realism
        carb.settings.get_settings().set("/rtx/reflections/enable", False)
        carb.settings.get_settings().set("/rtx/refractions/enable", False)
        carb.settings.get_settings().set("/rtx/globalIllumination/enable", False)

        # Enable texture streaming for large scenes
        carb.settings.get_settings().set("/renderer/textureStreaming/enabled", True)
        carb.settings.get_settings().set("/renderer/textureStreaming/targetMemory", 1073741824)  # 1GB

def setup_high_throughput_pipeline():
    """Setup Isaac Sim for high-throughput synthetic data generation"""

    optimizer = BatchProcessingOptimizer()
    optimizer.configure_batch_settings()
    optimizer.setup_memory_management()
    optimizer.optimize_for_throughput()

    print("High-throughput pipeline configured successfully")

    # Display optimization summary
    print("\nOptimization Summary:")
    print("- Resolution: 640x480 (balanced)")
    print("- Shadows: Enabled (for realism)")
    print("- Reflections: Disabled (for speed)")
    print("- GI: Disabled (for speed)")
    print("- Texture streaming: Enabled")
    print("- Anti-aliasing: Disabled")

if __name__ == "__main__":
    setup_high_throughput_pipeline()
```

## Integration with ROS 2

### Isaac ROS Bridge Configuration

```bash
# Install Isaac ROS Bridge
sudo apt update
sudo apt install -y ros-humble-isaac-ros-gem ros-humble-isaac-ros-image-ros-bridge

# Verify installation
dpkg -l | grep isaac-ros
```

### ROS 2 Integration Script

```python
# ros2_integration.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
import numpy as np
import cv2
from PIL import Image as PILImage
import torch
from omni.isaac.core import World
from omni.isaac.synthetic_utils import SyntheticDataHelper

class IsaacSimROS2Bridge(Node):
    def __init__(self):
        super().__init__('isaac_sim_ros2_bridge')

        # Publishers for synthetic sensor data
        self.rgb_pub = self.create_publisher(Image, '/camera/rgb/image_raw', 10)
        self.depth_pub = self.create_publisher(Image, '/camera/depth/image_raw', 10)
        self.camera_info_pub = self.create_publisher(CameraInfo, '/camera/rgb/camera_info', 10)

        # Subscribers for control commands
        self.command_sub = self.create_subscription(
            String,
            '/isaac_sim_commands',
            self.command_callback,
            10
        )

        # Isaac Sim components
        self.world = World(stage_units_in_meters=1.0)
        self.sd_helper = SyntheticDataHelper()

        # Camera configuration
        self.camera_resolution = (640, 480)
        self.camera_fov = 60.0  # degrees

        # Timer for data publishing
        self.timer = self.create_timer(0.1, self.publish_sensor_data)  # 10Hz

        self.get_logger().info('Isaac Sim ROS2 Bridge initialized')

    def command_callback(self, msg):
        """Handle incoming commands from ROS2"""
        command = msg.data
        self.get_logger().info(f'Received command: {command}')

        # Process command (e.g., move robot, change scene, etc.)
        if command.startswith('move_robot'):
            self.move_robot(command)
        elif command.startswith('change_scene'):
            self.change_scene(command)
        elif command.startswith('capture_data'):
            self.capture_synthetic_data()

    def publish_sensor_data(self):
        """Capture and publish synthetic sensor data"""
        try:
            # Step the simulation
            self.world.step(render=True)

            # Get synthetic data from Isaac Sim
            rgb_data = self.get_rgb_image()
            depth_data = self.get_depth_image()
            camera_info = self.get_camera_info()

            # Convert to ROS2 messages
            rgb_msg = self.numpy_to_ros_image(rgb_data, 'rgb8')
            depth_msg = self.numpy_to_ros_image(depth_data, '32FC1')

            # Set timestamps
            timestamp = self.get_clock().now().to_msg()
            rgb_msg.header.stamp = timestamp
            rgb_msg.header.frame_id = 'camera_rgb_optical_frame'

            depth_msg.header.stamp = timestamp
            depth_msg.header.frame_id = 'camera_depth_optical_frame'

            # Publish data
            self.rgb_pub.publish(rgb_msg)
            self.depth_pub.publish(depth_msg)
            self.camera_info_pub.publish(camera_info)

        except Exception as e:
            self.get_logger().error(f'Error publishing sensor data: {e}')

    def get_rgb_image(self):
        """Get RGB image from Isaac Sim"""
        # This would interface with Isaac Sim's rendering system
        # In practice, you'd use the SyntheticDataHelper to get RGB data
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def get_depth_image(self):
        """Get depth image from Isaac Sim"""
        # This would interface with Isaac Sim's depth rendering
        return np.random.rand(480, 640).astype(np.float32) * 10.0  # 0-10 meters

    def get_camera_info(self):
        """Get camera info for ROS2"""
        info = CameraInfo()
        info.header.frame_id = 'camera_rgb_optical_frame'
        info.width = self.camera_resolution[0]
        info.height = self.camera_resolution[1]

        # Calculate intrinsic parameters
        focal_length = (self.camera_resolution[0] / 2) / np.tan(np.radians(self.camera_fov / 2))
        info.k = [focal_length, 0.0, self.camera_resolution[0]/2,
                  0.0, focal_length, self.camera_resolution[1]/2,
                  0.0, 0.0, 1.0]

        return info

    def numpy_to_ros_image(self, numpy_img, encoding):
        """Convert numpy array to ROS Image message"""
        from cv_bridge import CvBridge
        bridge = CvBridge()
        return bridge.cv2_to_imgmsg(numpy_img, encoding=encoding)

    def move_robot(self, command):
        """Move robot based on command"""
        # Implementation would move the simulated robot
        self.get_logger().info(f'Moving robot: {command}')

    def change_scene(self, command):
        """Change scene based on command"""
        # Implementation would modify the simulated environment
        self.get_logger().info(f'Changing scene: {command}')

    def capture_synthetic_data(self):
        """Capture synthetic training data"""
        self.get_logger().info('Capturing synthetic data...')

def main(args=None):
    rclpy.init(args=args)

    bridge = IsaacSimROS2Bridge()

    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        bridge.get_logger().info('Shutting down Isaac Sim ROS2 Bridge')
    finally:
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Troubleshooting and Common Issues

### GPU Memory Issues

```bash
# Check GPU memory usage
nvidia-smi

# Increase GPU heap size if needed
export ISAACSIM_HEADLESS=1  # Run in headless mode to save memory

# Reduce rendering resolution for memory conservation
carb.settings.get_settings().set("/renderer/resolution/width", 320)
carb.settings.get_settings().set("/renderer/resolution/height", 240)
```

### Performance Optimization Tips

1. **Use Headless Mode**: For pure data generation without visualization
2. **Reduce Scene Complexity**: Simplify geometries for faster rendering
3. **Batch Processing**: Process multiple samples in parallel
4. **Memory Management**: Clear caches periodically during long runs
5. **GPU Utilization**: Monitor GPU usage and adjust settings accordingly

### Common Configuration Issues

```bash
# If CUDA operations fail
export CUDA_LAUNCH_BLOCKING=1

# If rendering is slow
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json

# If Isaac Sim won't start
pkill -f IsaacSim
nvidia-smi -r  # Reset GPU if needed
```

## Validation and Testing

### Configuration Validation Script

```python
# validate_installation.py
import subprocess
import sys
import os

def validate_isaac_sim_installation():
    """Validate Isaac Sim installation and configuration"""

    print("Validating Isaac Sim Installation...")

    # Check if Isaac Sim Python modules are accessible
    try:
        import omni
        import omni.isaac.core
        print("✓ Isaac Sim Python modules accessible")
    except ImportError as e:
        print(f"✗ Isaac Sim Python modules not found: {e}")
        return False

    # Check GPU availability
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name()}")
        else:
            print("✗ CUDA not available")
            return False
    except ImportError:
        print("✗ PyTorch not installed - install with: pip install torch")
        return False

    # Check Isaac Sim executable (if using standalone)
    try:
        result = subprocess.run(['which', 'isaac-sim'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Isaac Sim executable found: {result.stdout.strip()}")
        else:
            print("? Isaac Sim executable not found (using Omniverse Launcher)")
    except Exception as e:
        print(f"? Could not check executable: {e}")

    # Check NVIDIA drivers
    try:
        result = subprocess.run(['nvidia-smi', '-q'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ NVIDIA drivers accessible")
        else:
            print("✗ NVIDIA drivers not accessible")
            return False
    except FileNotFoundError:
        print("✗ nvidia-smi not found - check NVIDIA driver installation")
        return False

    print("\nInstallation validation completed successfully!")
    return True

def validate_synthetic_data_pipeline():
    """Validate synthetic data generation pipeline"""

    print("\nValidating Synthetic Data Pipeline...")

    try:
        from omni.isaac.synthetic_utils import SyntheticDataHelper
        print("✓ Synthetic Data Helper accessible")
    except ImportError as e:
        print(f"✗ Synthetic Data Helper not accessible: {e}")
        return False

    try:
        from omni.isaac.core import World
        world = World(stage_units_in_meters=1.0)
        print("✓ Isaac Sim World accessible")
        world.clear()
    except Exception as e:
        print(f"✗ Isaac Sim World not accessible: {e}")
        return False

    print("Synthetic data pipeline validation completed!")
    return True

if __name__ == "__main__":
    success = validate_isaac_sim_installation()
    if success:
        validate_synthetic_data_pipeline()
    else:
        print("\nInstallation validation failed. Please check the installation guide.")
        sys.exit(1)
```

This comprehensive setup guide provides the foundation for using Isaac Sim to generate synthetic data for humanoid robot perception systems, enabling the development of robust vision-language-action capabilities through photorealistic simulation.