---
sidebar_position: 4
---

# Human-Aware Navigation for Humanoid Robots

## Social Navigation Fundamentals

Human-aware navigation is crucial for humanoid robots that operate in human-populated environments. This chapter covers the implementation of socially-aware navigation systems that respect personal space, exhibit appropriate social behaviors, and navigate safely around humans.

### Proxemics Theory Implementation

Proxemics, developed by anthropologist Edward T. Hall, defines four distance zones that govern human spatial interactions:

1. **Intimate Distance** (0-45 cm): Reserved for close relationships and physical contact
2. **Personal Distance** (45-120 cm): For interactions among friends and family members
3. **Social Distance** (120-360 cm): For casual acquaintances and strangers
4. **Public Distance** (360+ cm): For formal interactions and public speaking

For humanoid robots, respecting these distances is essential for natural human-robot interaction. The robot should maintain appropriate distances based on the context and relationship with nearby humans.

```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <nav_msgs/msg/occupancy_grid.hpp>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <cmath>
#include <vector>
#include <algorithm>

namespace nav2_social_navigation {

// Proxemic distance thresholds in meters
const double INTIMATE_DISTANCE_MAX = 0.45;
const double PERSONAL_DISTANCE_MIN = 0.45;
const double PERSONAL_DISTANCE_MAX = 1.2;
const double SOCIAL_DISTANCE_MIN = 1.2;
const double SOCIAL_DISTANCE_MAX = 3.6;
const double PUBLIC_DISTANCE_MIN = 3.6;

enum class ProxemicZone {
  INTIMATE,  // Very close, typically for intimate relationships
  PERSONAL,  // Close but comfortable for friends/family
  SOCIAL,    // Comfortable distance for strangers/acquaintances
  PUBLIC     // Formal distance for public interactions
};

/**
 * @brief Class to manage proxemic spaces around humans
 */
class ProxemicSpaceManager : public rclcpp::Node
{
public:
  explicit ProxemicSpaceManager(const rclcpp::NodeOptions & options);

  /**
   * @brief Determines the proxemic zone between robot and human
   * @param distance Distance between robot and human in meters
   * @return ProxemicZone enum value
   */
  ProxemicZone getProxemicZone(double distance) const;

  /**
   * @brief Checks if the robot is violating human personal space
   * @param distance Distance between robot and human in meters
   * @return True if space violation detected
   */
  bool isSpaceViolation(double distance) const;

private:
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
  rclcpp::Publisher<nav_msgs::msg::OccupancyGrid>::SharedPtr social_costmap_pub_;

  void scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr msg);
};

} // namespace nav2_social_navigation
```

### Human Detection and Tracking

Robust human detection and tracking form the foundation of human-aware navigation. The system must detect humans reliably and track their positions and movements over time.

```cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <geometry_msgs/msg/pose_array.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>
#include <tf2_ros/transform_listener.h>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <vector>
#include <memory>
#include <unordered_map>

namespace nav2_social_navigation {

struct HumanDetection {
  geometry_msgs::msg::Pose pose;
  double confidence;
  int id;
  rclcpp::Time last_seen;
};

/**
 * @brief Class to detect and track humans in the environment
 */
class HumanDetectorTracker : public rclcpp::Node
{
public:
  explicit HumanDetectorTracker(const rclcpp::NodeOptions & options);

  /**
   * @brief Process incoming sensor data to detect humans
   * @param image_msg RGB image from robot's camera
   * @param depth_msg Depth image for 3D pose estimation
   * @return Vector of detected humans with poses
   */
  std::vector<HumanDetection> detectHumans(
    const sensor_msgs::msg::Image::SharedPtr image_msg,
    const sensor_msgs::msg::Image::SharedPtr depth_msg);

  /**
   * @brief Update human tracking with new detections
   * @param detections New human detections
   * @return Updated list of tracked humans with IDs
   */
  std::vector<HumanDetection> updateTracking(
    const std::vector<HumanDetection>& detections);

  /**
   * @brief Get currently tracked humans
   * @return Vector of currently tracked humans
   */
  std::vector<HumanDetection> getTrackedHumans() const;

private:
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr rgb_sub_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr depth_sub_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr laser_sub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseArray>::SharedPtr detections_pub_;

  std::unordered_map<int, HumanDetection> tracked_humans_;
  int next_human_id_;
  tf2_ros::Buffer tf_buffer_;
  tf2_ros::TransformListener tf_listener_;

  cv::dnn::Net detection_net_;
  void initializeDetectionNetwork();
  std::vector<cv::Mat> preprocessImage(const cv::Mat& image);
  std::vector<HumanDetection> postprocessDetections(
    const std::vector<cv::Mat>& outputs,
    const cv::Size& original_size);
};

} // namespace nav2_social_navigation
```

### Social Force Model

The social force model treats navigation as a physics simulation where humans and robots exert "forces" on each other. This creates natural-looking avoidance behaviors that respect social norms.

```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <vector>
#include <cmath>

namespace nav2_social_navigation {

/**
 * @brief Physics-based model for social interaction forces
 */
class SocialForceModel : public rclcpp::Node
{
public:
  explicit SocialForceModel(const rclcpp::NodeOptions & options);

  /**
   * @brief Calculates the repulsive force from a human based on proxemics
   * @param robot_pose Current pose of the robot
   * @param human_pose Pose of the detected human
   * @return Force vector representing the social repulsion
   */
  geometry_msgs::msg::Vector3 calculateHumanRepulsiveForce(
    const geometry_msgs::msg::Pose& robot_pose,
    const geometry_msgs::msg::Pose& human_pose);

  /**
   * @brief Calculates group repulsive forces for multiple humans
   * @param robot_pose Current pose of the robot
   * @param humans Vector of detected human poses
   * @return Combined force vector from all humans
   */
  geometry_msgs::msg::Vector3 calculateGroupRepulsiveForces(
    const geometry_msgs::msg::Pose& robot_pose,
    const std::vector&lt;geometry_msgs::msg::Pose&gt;& humans);

  /**
   * @brief Updates the social force field around the robot
   * @param humans Vector of detected human poses
   * @return Updated force field for path planning
   */
  std::vector&lt;geometry_msgs::msg::Vector3&gt; updateSocialForceField(
    const std::vector&lt;geometry_msgs::msg::Pose&gt;& humans);
};

} // namespace nav2_social_navigation
```

## Human-Aware Path Planning

Human-aware path planning integrates social constraints into traditional path planning algorithms. The robot must find paths that not only reach the goal efficiently but also respect human comfort zones and social norms.

```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/poseStamped.hpp>
#include <nav_msgs/msg/path.hpp>
#include <nav2_core/global_planner.hpp>
#include <nav2_costmap_2d/costmap_2d_ros.hpp>
#include <vector>
#include <memory>

namespace nav2_social_navigation {

/**
 * @brief Human-aware path planner that respects social norms
 */
class HumanAwarePathPlanner : public nav2_core::GlobalPlanner
{
public:
  HumanAwarePathPlanner() = default;
  ~HumanAwarePathPlanner() = default;

  void configure(
    rclcpp_lifecycle::LifecycleNode::SharedPtr node,
    std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;

  void cleanup() override;
  void activate() override;
  void deactivate() override;

  nav_msgs::msg::Path createPlan(
    const geometry_msgs::msg::PoseStamped& start,
    const geometry_msgs::msg::PoseStamped& goal) override;

private:
  rclcpp_lifecycle::LifecycleNode::SharedPtr node_;
  std::string name_;
  std::shared_ptr<tf2_ros::Buffer> tf_;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros_;

  // Social costmap for human-aware planning
  nav2_costmap_2d::Costmap2D social_costmap_;

  // Parameters for social navigation
  double social_radius_;
  double social_force_coefficient_;
  double personal_space_weight_;
  double path_efficiency_weight_;

  // Subscriptions for human detection
  rclcpp::Subscription<geometry_msgs::msg::PoseArray>::SharedPtr human_detection_sub_;

  // Currently detected humans
  std::vector<geometry_msgs::msg::Pose> current_humans_;

  /**
   * @brief Updates social costmap based on human positions
   * @param humans Vector of detected human positions
   */
  void updateSocialCostmap(const std::vector&lt;geometry_msgs::msg::Pose&gt;& humans);

  /**
   * @brief Modifies the global costmap with social constraints
   * @param original_cost Original costmap
   * @param social_cost Social costmap overlay
   * @return Combined costmap with social constraints
   */
  void combineCostmaps(
    nav2_costmap_2d::Costmap2D& original_cost,
    const nav2_costmap_2d::Costmap2D& social_cost);

  /**
   * @brief Callback for human detection updates
   * @param msg Pose array of detected humans
   */
  void humanDetectionCallback(const geometry_msgs::msg::PoseArray::SharedPtr msg);

  /**
   * @brief Calculates social cost at a specific cell
   * @param mx Map x coordinate
   * @param my Map y coordinate
   * @param humans Vector of human positions
   * @return Social cost value
   */
  double calculateSocialCostAtCell(
    unsigned int mx, unsigned int my,
    const std::vector&lt;geometry_msgs::msg::Pose&gt;& humans) const;

  /**
   * @brief Modifies A* heuristic to consider social factors
   * @param current Current cell
   * @param goal Goal cell
   * @param humans Current human positions
   * @return Modified heuristic value
   */
  double socialAwareHeuristic(
    const geometry_msgs::msg::Point& current,
    const geometry_msgs::msg::Point& goal,
    const std::vector&lt;geometry_msgs::msg::Pose&gt;& humans) const;
};

} // namespace nav2_social_navigation
```

## Footstep-Aware Path Planning

For humanoid robots, path planning must consider the discrete nature of bipedal locomotion. The footstep-aware path planning algorithm generates paths that are compatible with the robot's walking gait and stepping constraints.

```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose2_d.hpp>
#include <visualization_msgs/msg/marker_array.hpp>
#include <vector>
#include <queue>

namespace nav2_social_navigation {

struct Footstep {
  geometry_msgs::msg::Pose2D position;
  double orientation;
  bool is_left_foot;
  double support_polygon_area;  // Area of support polygon when this foot is placed
  bool is_anchored;             // Whether this foot is part of the support polygon
};

struct SupportPolygon {
  std::vector<geometry_msgs::msg::Pose2D> feet;
  geometry_msgs::msg::Point center_of_support;
  double area;
  bool isValid() const { return area > 0.01; } // Minimum support area threshold
};

/**
 * @brief Footstep planning considering human presence
 */
class FootstepAwarePlanner
{
public:
  FootstepAwarePlanner(double step_width, double step_length, double max_step_height);

  /**
   * @brief Plans footsteps to reach goal while avoiding humans
   * @param start Start position
   * @param goal Goal position
   * @param humans Detected human positions
   * @param path Output path as sequence of footsteps
   * @return True if successful
   */
  bool planFootsteps(
    const geometry_msgs::msg::Pose2D& start,
    const geometry_msgs::msg::Pose2D& goal,
    const std::vector&lt;geometry_msgs::msg::Pose2D&gt;& humans,
    std::vector<Footstep>& path);

  /**
   * @brief Generates candidate footsteps for current stance foot
   * @param stance_foot Current stance foot position
   * @param swing_foot_type Type of foot to swing next (left or right)
   * @return Vector of candidate footsteps
   */
  std::vector<Footstep> generateCandidateFootsteps(
    const Footstep& stance_foot,
    bool is_next_left_foot) const;

  /**
   * @brief Validates support polygon stability for a given footstep
   * @param current_support Current support polygon
   * @param new_footstep New footstep to add
   * @return True if resulting support polygon is stable
   */
  bool isStableSupportPolygon(
    const SupportPolygon& current_support,
    const Footstep& new_footstep) const;

private:
  double step_width_, step_length_, max_step_height_;
  double social_distance_threshold_;
  double robot_width_, robot_length_;  // Robot dimensions for collision checking
  double min_support_margin_;          // Minimum margin for stable support

  /**
   * @brief Validates if a footstep is stable and safe
   * @param footstep Proposed footstep
   * @param humans Human positions to avoid
   * @return True if footstep is valid
   */
  bool isValidFootstep(
    const Footstep& footstep,
    const std::vector&lt;geometry_msgs::msg::Pose2D&gt;& humans) const;

  /**
   * @brief Validates if a footstep is collision-free
   * @param footstep Proposed footstep
   * @param humans Human positions
   * @return True if no collisions detected
   */
  bool isCollisionFreeFootstep(
    const Footstep& footstep,
    const std::vector&lt;geometry_msgs::msg::Pose2D&gt;& humans) const;

  /**
   * @brief Calculates cost of a footstep considering humans
   * @param footstep Proposed footstep
   * @param humans Human positions
   * @return Cost value
   */
  double calculateFootstepCost(
    const Footstep& footstep,
    const std::vector&lt;geometry_msgs::msg::Pose2D&gt;& humans) const;

  /**
   * @brief Calculates social cost component of footstep
   * @param footstep Proposed footstep
   * @param humans Human positions
   * @return Social cost value
   */
  double calculateSocialCost(
    const Footstep& footstep,
    const std::vector&lt;geometry_msgs::msg::Pose2D&gt;& humans) const;

  /**
   * @brief Calculates stability cost based on support polygon
   * @param footstep Proposed footstep
   * @param current_support Current support polygon
   * @return Stability cost value
   */
  double calculateStabilityCost(
    const Footstep& footstep,
    const SupportPolygon& current_support) const;

  /**
   * @brief Calculates efficiency cost based on progress toward goal
   * @param footstep Proposed footstep
   * @param goal Goal position
   * @return Efficiency cost value
   */
  double calculateEfficiencyCost(
    const Footstep& footstep,
    const geometry_msgs::msg::Pose2D& goal) const;

  /**
   * @brief Performs footstep planning using A* search
   * @param start Starting footstep configuration
   * @param goal Goal position
   * @param humans Human positions
   * @param path Output path of footsteps
   * @return True if path found
   */
  bool planFootstepsAStar(
    const std::vector<Footstep>& start_config,
    const geometry_msgs::msg::Pose2D& goal,
    const std::vector&lt;geometry_msgs::msg::Pose2D&gt;& humans,
    std::vector<Footstep>& path);
};

} // namespace nav2_social_navigation
```

## Integration with Navigation Stack

The human-aware navigation system integrates seamlessly with the Navigation2 stack through custom plugins and behavior trees. This allows the robot to switch between normal navigation and socially-aware navigation based on the environment.

```yaml
# social_navigation_params.yaml
local_costmap:
  local_costmap:
    ros__parameters:
      plugins: ["social_layer", "voxel_layer", "inflation_layer"]
      social_layer:
        plugin: "nav2_social_layer::SocialLayer"
        enabled: true
        social_radius: 1.0
        social_force_coefficient: 2.0
        human_detection_topic: "/human_detector/detections"

global_costmap:
  global_costmap:
    ros__parameters:
      plugins: ["social_layer", "static_layer", "obstacle_layer", "inflation_layer"]
      social_layer:
        plugin: "nav2_social_layer::SocialLayer"
        enabled: true
        social_radius: 2.0
        social_force_coefficient: 1.5
        human_detection_topic: "/human_detector/detections"

behavior_tree_xml_filename: "social_nav_tree.xml"
```

The behavior tree for social navigation includes additional nodes to handle social situations:

```xml
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>
      <SmoothPath path="{path}" smoother_id="simple_smoother" max_deviation="0.3"/>
      <FollowPath path="{path}" controller_id="FollowPath"/>
    </Sequence>
  </BehaviorTree>

  <BehaviorTree ID="SocialNavTree">
    <ReactiveSequence>
      <IsHumanNearby min_distance="2.0"/>
      <Fallback>
        <Sequence>
          <WaitForHumanToPass timeout="10.0"/>
          <ComputePathToPose goal="{goal}" path="{path}" planner_id="HumanAwarePlanner"/>
        </Sequence>
        <Sequence>
          <ComputePathToPose goal="{goal}" path="{path}" planner_id="HumanAwarePlanner"/>
          <SmoothPath path="{path}" smoother_id="simple_smoother" max_deviation="0.3"/>
          <FollowPath path="{path}" controller_id="FollowPath"/>
        </Sequence>
      </Fallback>
    </ReactiveSequence>
  </BehaviorTree>
</root>
```

## Practical Implementation Example

Here's a complete example of how to implement and use the human-aware navigation system in a humanoid robot application:

```cpp
#include <rclcpp/rclcpp.hpp>
#include <nav2_msgs/action/navigate_to_pose.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <memory>

class SocialNavigationDemo : public rclcpp::Node
{
public:
  SocialNavigationDemo() : Node("social_navigation_demo")
  {
    // Initialize human detector and tracker
    human_detector_ = std::make_shared<nav2_social_navigation::HumanDetectorTracker>(
      rclcpp::NodeOptions());

    // Initialize social force model
    social_force_model_ = std::make_shared<nav2_social_navigation::SocialForceModel>(
      rclcpp::NodeOptions());

    // Initialize human-aware path planner
    human_aware_planner_ = std::make_shared<nav2_social_navigation::HumanAwarePathPlanner>();

    // Initialize navigation client
    nav_client_ = rclcpp_action::create_client<nav2_msgs::action::NavigateToPose>(
      this, "navigate_to_pose");
  }

  void navigateWithSocialAwareness(const geometry_msgs::msg::PoseStamped& goal)
  {
    // Get current human detections
    auto humans = human_detector_->getTrackedHumans();

    // Calculate social forces
    auto social_forces = social_force_model_->updateSocialForceField(
      convertToPoseVector(humans));

    // Create custom planner with social constraints
    auto social_costmap = createSocialCostmap(social_forces);

    // Update navigation parameters based on social context
    if (!humans.empty()) {
      RCLCPP_INFO(get_logger(), "Humans detected, using social navigation mode");
      // Switch to human-aware navigation
      configureSocialNavigation();
    } else {
      RCLCPP_INFO(get_logger(), "No humans detected, using normal navigation");
      // Use normal navigation
      configureNormalNavigation();
    }

    // Send navigation goal
    auto goal_handle = sendNavigationGoal(goal);

    // Monitor navigation progress and adjust for dynamic human positions
    monitorNavigationWithSocialAwareness(goal_handle, humans);
  }

private:
  std::shared_ptr<nav2_social_navigation::HumanDetectorTracker> human_detector_;
  std::shared_ptr<nav2_social_navigation::SocialForceModel> social_force_model_;
  std::shared_ptr<nav2_social_navigation::HumanAwarePathPlanner> human_aware_planner_;
  rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SharedPtr nav_client_;

  void configureSocialNavigation()
  {
    // Set parameters for social navigation
    // Increase personal space radius
    // Adjust speed to be more cautious around humans
    // Enable social costmap layer
  }

  void configureNormalNavigation()
  {
    // Set parameters for normal navigation
    // Use default collision avoidance
    // Higher speed limits
  }

  rclcpp_action::ClientGoalHandle<nav2_msgs::action::NavigateToPose>::SharedPtr
  sendNavigationGoal(const geometry_msgs::msg::PoseStamped& goal)
  {
    auto goal_msg = nav2_msgs::action::NavigateToPose::Goal();
    goal_msg.pose = goal;

    auto send_goal_options = rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SendGoalOptions();
    send_goal_options.result_callback = [this](const auto& result) {
      RCLCPP_INFO(get_logger(), "Navigation completed with status: %d", result.code);
    };

    return nav_client_->async_send_goal(goal_msg, send_goal_options);
  }

  void monitorNavigationWithSocialAwareness(
    rclcpp_action::ClientGoalHandle<nav2_msgs::action::NavigateToPose>::SharedPtr goal_handle,
    const std::vector<nav2_social_navigation::HumanDetection>& humans)
  {
    // Continuously monitor for new human detections during navigation
    // Adjust path if humans move into the robot's path
    // Consider stopping or rerouting if humans get too close
  }

  std::vector<geometry_msgs::msg::Pose> convertToPoseVector(
    const std::vector<nav2_social_navigation::HumanDetection>& detections)
  {
    std::vector<geometry_msgs::msg::Pose> poses;
    for (const auto& detection : detections) {
      poses.push_back(detection.pose);
    }
    return poses;
  }

  nav2_costmap_2d::Costmap2D createSocialCostmap(
    const std::vector<geometry_msgs::msg::Vector3>& forces)
  {
    // Create costmap based on social forces
    // Higher costs near humans to maintain appropriate distance
    nav2_costmap_2d::Costmap2D social_costmap;
    // Implementation details...
    return social_costmap;
  }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);

  auto demo = std::make_shared<SocialNavigationDemo>();

  // Example navigation goal
  geometry_msgs::msg::PoseStamped goal;
  goal.header.frame_id = "map";
  goal.pose.position.x = 5.0;
  goal.pose.position.y = 3.0;
  goal.pose.position.z = 0.0;
  goal.pose.orientation.w = 1.0;

  // Navigate with social awareness
  demo->navigateWithSocialAwareness(goal);

  rclcpp::spin(demo);
  rclcpp::shutdown();
  return 0;
}
```

## Testing and Validation

Testing human-aware navigation requires realistic simulation scenarios with multiple humans moving in various patterns. The system should be validated for:

1. **Social Compliance**: Does the robot respect personal space and social norms?
2. **Safety**: Are collisions avoided and does the robot maintain safe distances?
3. **Efficiency**: Can the robot still reach goals efficiently while being socially aware?
4. **Naturalness**: Do the robot's movements appear natural and predictable to humans?

A comprehensive test suite should include scenarios such as:
- Single human crossing the robot's path
- Multiple humans walking in formation
- Humans standing in groups
- Humans approaching the robot directly
- Dynamic environments with changing human positions

The validation process should measure metrics like social distance violations, path efficiency, and human comfort ratings to ensure the system performs appropriately in human environments.

## Summary

Human-aware navigation is essential for humanoid robots operating in human-populated environments. By implementing proxemics theory, social force models, and human-aware path planning, robots can navigate safely and naturally around humans while respecting social norms and personal space. The integration with Navigation2 provides a robust framework for deploying these capabilities in real-world applications.