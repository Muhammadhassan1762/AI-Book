# Data Model: The AI-Robot Brain (NVIDIA Isaac™)

**Feature**: 003-ai-robot-brain
**Created**: 2025-12-15
**Status**: Complete

## Entity: Synthetic Dataset

**Description**: Collection of RGB, Depth, and Segmentation images with annotations for training perception models

**Attributes**:
- `dataset_id`: Unique identifier for the dataset
- `name`: Human-readable name for the dataset
- `description`: Brief description of the dataset contents
- `creation_date`: Timestamp when dataset was generated
- `image_count`: Total number of images in the dataset
- `modalities`: List of available modalities (RGB, Depth, Segmentation)
- `annotations`: Type of annotations available (bounding boxes, masks, keypoints)
- `scene_config`: Configuration parameters for the Isaac Sim scene
- `camera_params`: Camera intrinsic and extrinsic parameters

**Relationships**:
- Contains many `Synthetic Image` entities
- Associated with one `Isaac Sim Scene` configuration

## Entity: Synthetic Image

**Description**: Individual image from synthetic dataset with metadata

**Attributes**:
- `image_id`: Unique identifier for the image
- `dataset_id`: Reference to parent dataset
- `image_type`: Type of image (RGB, Depth, Segmentation)
- `file_path`: Path to the image file
- `timestamp`: When the image was captured in simulation
- `camera_pose`: 6D pose of the camera when image was captured
- `annotations`: Associated annotation data
- `width`: Image width in pixels
- `height`: Image height in pixels

**Relationships**:
- Belongs to one `Synthetic Dataset`
- Associated with one `Camera Configuration`

## Entity: VSLAM Map

**Description**: Spatial representation of the environment generated from visual inputs

**Attributes**:
- `map_id`: Unique identifier for the map
- `name`: Human-readable name for the map
- `description`: Brief description of the mapped environment
- `creation_date`: Timestamp when map was generated
- `map_type`: Type of map (2D Occupancy Grid, 3D Point Cloud, Mesh)
- `resolution`: Spatial resolution of the map
- `origin_pose`: Pose of the map origin in world coordinates
- `bounds`: Bounding box of the mapped area
- `coverage_percentage`: Percentage of area successfully mapped
- `quality_score`: Quality metric for the generated map

**Relationships**:
- Contains many `Map Feature` entities
- Associated with one `Robot Trajectory`
- Generated from many `Camera Frame` entities

## Entity: Map Feature

**Description**: Individual feature detected and mapped by VSLAM system

**Attributes**:
- `feature_id`: Unique identifier for the feature
- `map_id`: Reference to parent map
- `feature_type`: Type of feature (point, line, plane, landmark)
- `position`: 3D position of the feature
- `descriptor`: Feature descriptor for matching
- `confidence`: Confidence level of the feature detection
- `observations`: Number of times this feature was observed

**Relationships**:
- Belongs to one `VSLAM Map`

## Entity: Robot Trajectory

**Description**: Path and pose history of the robot during mapping

**Attributes**:
- `trajectory_id`: Unique identifier for the trajectory
- `map_id`: Reference to associated map
- `start_time`: When trajectory recording started
- `end_time`: When trajectory recording ended
- `total_distance`: Total distance traveled
- `waypoints`: Sequence of poses along the trajectory
- `pose_timestamps`: Timestamps for each pose in the trajectory

**Relationships**:
- Associated with one `VSLAM Map`
- Contains many `Robot Pose` entities

## Entity: Robot Pose

**Description**: Individual pose along the robot trajectory

**Attributes**:
- `pose_id`: Unique identifier for the pose
- `trajectory_id`: Reference to parent trajectory
- `timestamp`: When this pose was recorded
- `position`: 3D position (x, y, z)
- `orientation`: Orientation as quaternion (x, y, z, w)
- `covariance`: Uncertainty in pose estimation
- `frame_id`: Coordinate frame of the pose

**Relationships**:
- Belongs to one `Robot Trajectory`

## Entity: Navigation Plan

**Description**: Planned path from start to goal that accounts for obstacles

**Attributes**:
- `plan_id`: Unique identifier for the plan
- `map_id`: Reference to the map used for planning
- `start_pose`: Starting pose for navigation
- `goal_pose`: Target pose for navigation
- `global_path`: Sequence of waypoints from start to goal
- `plan_time`: When the plan was created
- `plan_validity`: Whether the plan is still valid
- `execution_status`: Current status of plan execution

**Relationships**:
- Associated with one `VSLAM Map`
- Contains many `Navigation Waypoint` entities

## Entity: Navigation Waypoint

**Description**: Individual waypoint in the navigation plan

**Attributes**:
- `waypoint_id`: Unique identifier for the waypoint
- `plan_id`: Reference to parent navigation plan
- `sequence_number`: Order in the navigation sequence
- `pose`: Target pose for this waypoint
- `tolerance`: Acceptable tolerance for reaching this waypoint
- `actions`: Actions to perform at this waypoint
- `status`: Execution status (pending, reached, failed)

**Relationships**:
- Belongs to one `Navigation Plan`

## Entity: Isaac Sim Scene

**Description**: Configuration for Isaac Sim environment used for data generation

**Attributes**:
- `scene_id`: Unique identifier for the scene
- `name`: Human-readable name for the scene
- `description`: Description of the scene layout
- `objects`: List of objects in the scene
- `lighting_config`: Lighting parameters
- `camera_config`: Camera placement and parameters
- `material_properties`: Material properties for realistic rendering
- `physics_properties`: Physics simulation parameters

**Relationships**:
- Used to generate many `Synthetic Dataset` entities