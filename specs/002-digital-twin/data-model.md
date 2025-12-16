# Data Model: The Digital Twin (Gazebo & Unity)

## Digital Twin Entity
- **Name**: Digital twin representation
- **Fields**:
  - twin_id: unique identifier for the digital twin
  - physical_counterpart: reference to the real-world robot or system
  - simulation_environment: Gazebo world file path
  - visual_environment: Unity scene file path
  - synchronization_state: current sync status with physical system
  - last_update: timestamp of last data update
- **Relationships**: Links to physics model, visual model, and sensor models
- **Validation rules**: Must have both simulation and visual environments defined

## Physics Model Entity
- **Name**: Physics representation in Gazebo
- **Fields**:
  - model_name: name of the physics model
  - mass_properties: mass, center of mass, inertia tensor
  - collision_geometry: mesh or primitive shapes for collision detection
  - friction_coefficients: static and dynamic friction values
  - damping_factors: linear and angular damping coefficients
- **Relationships**: Connected to visual model through URDF/robot description
- **Validation rules**: Mass must be positive, inertia tensor must be physically valid

## Visual Model Entity
- **Name**: Visual representation in Unity
- **Fields**:
  - asset_name: name of the Unity asset
  - materials: list of material properties for rendering
  - textures: list of texture maps (diffuse, normal, specular)
  - lighting_properties: reflectance, transparency, emission properties
  - level_of_detail: different mesh complexities for performance
- **Relationships**: Mirrors physics model geometry but optimized for rendering
- **Validation rules**: Must match physical dimensions within tolerance

## Sensor Simulation Entity
- **Name**: Simulated sensor in digital twin
- **Fields**:
  - sensor_type: LiDAR, depth camera, IMU, etc.
  - sensor_name: unique name for the sensor
  - position: 3D position relative to robot frame
  - orientation: 3D orientation relative to robot frame
  - noise_parameters: standard deviation, bias, drift characteristics
  - range_limits: minimum and maximum sensing range
  - field_of_view: angular field of view for camera sensors
- **Relationships**: Attached to physics and visual models
- **Validation rules**: Range limits must be physically plausible, noise parameters within realistic bounds

## LiDAR Sensor Entity
- **Name**: Simulated LiDAR sensor
- **Fields**:
  - rays_count: number of laser rays
  - range_min: minimum detection range
  - range_max: maximum detection range
  - resolution_horizontal: angular resolution in horizontal plane
  - resolution_vertical: angular resolution in vertical plane
  - noise_stddev: standard deviation of distance measurements
- **Relationships**: Inherits from Sensor Simulation entity
- **Validation rules**: Range_max must be greater than range_min, rays count must be reasonable

## Depth Camera Sensor Entity
- **Name**: Simulated depth camera sensor
- **Fields**:
  - image_width: width of the image in pixels
  - image_height: height of the image in pixels
  - fov_horizontal: horizontal field of view in degrees
  - fov_vertical: vertical field of view in degrees
  - depth_range_min: minimum depth measurement
  - depth_range_max: maximum depth measurement
  - noise_model: parameters for depth noise simulation
- **Relationships**: Inherits from Sensor Simulation entity
- **Validation rules**: Image dimensions must be valid, depth range must be positive

## IMU Sensor Entity
- **Name**: Simulated IMU sensor
- **Fields**:
  - accelerometer_noise_density: noise density for accelerometer (m/s^2/sqrt(Hz))
  - gyroscope_noise_density: noise density for gyroscope (rad/s/sqrt(Hz))
  - accelerometer_random_walk: bias random walk for accelerometer (m/s^3/sqrt(Hz))
  - gyroscope_random_walk: bias random walk for gyroscope (rad/s^2/sqrt(Hz))
  - update_rate: sensor update frequency in Hz
- **Relationships**: Inherits from Sensor Simulation entity
- **Validation rules**: Noise parameters must be positive, update rate must be reasonable

## Gazebo World Entity
- **Name**: Physics simulation environment
- **Fields**:
  - world_name: name of the world
  - gravity_vector: 3D gravity vector (typically [0, 0, -9.81])
  - physics_engine: name of physics engine (ODE, Bullet, etc.)
  - environment_objects: list of static objects in the world
  - lighting_conditions: ambient and directional light settings
- **Relationships**: Contains physics models and sensor models
- **Validation rules**: Gravity vector must have reasonable magnitude

## Unity Scene Entity
- **Name**: Visual simulation environment
- **Fields**:
  - scene_name: name of the Unity scene
  - rendering_pipeline: Built-in, URP, or HDRP
  - lighting_setup: static and dynamic lighting configuration
  - environment_assets: list of environmental objects
  - camera_settings: main camera configuration
- **Relationships**: Contains visual models and rendering elements
- **Validation rules**: Rendering pipeline must be supported version

## Simulation Bridge Entity
- **Name**: Communication layer between environments
- **Fields**:
  - bridge_type: ROS 2, custom protocol, or middleware type
  - message_formats: definition of message types exchanged
  - update_frequency: synchronization frequency between environments
  - data_mapping: mapping between physics and visual coordinate systems
  - latency_characteristics: communication delay parameters
- **Relationships**: Connects Gazebo world and Unity scene
- **Validation rules**: Update frequency must be reasonable for real-time performance