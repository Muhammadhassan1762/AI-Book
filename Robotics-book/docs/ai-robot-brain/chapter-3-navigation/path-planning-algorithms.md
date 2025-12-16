---
sidebar_position: 2
---

# Path Planning Algorithms for Humanoid Navigation

## Advanced Path Planning with Humanoid Constraints

Path planning for humanoid robots requires specialized algorithms that account for the unique kinematic and dynamic constraints of bipedal locomotion. Unlike wheeled robots, humanoid robots must consider foot placement, balance, and step sequencing in their navigation planning.

## Learning Objectives

By the end of this chapter, you will:
- Understand humanoid-specific path planning constraints
- Implement kinematically constrained path planners
- Design step-aware navigation algorithms
- Optimize paths for humanoid stability and safety
- Integrate semantic information into path planning
- Handle dynamic obstacle avoidance for humanoid navigation

## Humanoid-Specific Navigation Constraints

### Kinematic Constraints

Humanoid robots face unique kinematic constraints that must be considered in path planning:

1. **Foot Placement Constraints**: Steps must be placed on stable, traversable terrain
2. **Balance Constraints**: Center of mass must remain within support polygon
3. **Step Size Limits**: Maximum stride length and step height limitations
4. **Turning Radius**: Limited turning capability compared to wheeled robots
5. **Terrain Traversability**: Ability to handle stairs, slopes, and uneven terrain

### Dynamic Constraints

```cpp
// Humanoid kinematic constraints
struct HumanoidConstraints {
    // Step constraints
    double max_step_length = 0.3;      // Maximum step length (m)
    double max_step_width = 0.2;       // Maximum lateral step (m)
    double max_step_height = 0.15;     // Maximum step-up height (m)
    double min_step_length = 0.05;     // Minimum step length (m)

    // Balance constraints
    double com_height = 0.8;           // Center of mass height (m)
    double max_com_deviation = 0.05;   // Maximum CoM deviation (m)
    double support_polygon_radius = 0.15; // Support polygon radius (m)

    // Velocity constraints
    double max_linear_vel = 0.4;       // Max linear velocity (m/s)
    double max_angular_vel = 0.6;      // Max angular velocity (rad/s)
    double max_linear_acc = 0.5;       // Max linear acceleration (m/s²)
    double max_angular_acc = 1.0;      // Max angular acceleration (rad/s²)

    // Turning constraints
    double min_turning_radius = 0.3;   // Minimum turning radius (m)
    double step_turn_angle = 0.2;      // Max turn per step (rad)

    // Terrain constraints
    max_slope_angle = 20.0 * M_PI / 180.0;  // Max traversable slope (rad)
    max_roughness = 0.05;              // Max ground roughness (m)
};

class HumanoidPathPlanner {
private:
    HumanoidConstraints constraints_;
    std::unique_ptr<GridMap> traversability_map_;
    std::unique_ptr<StepSequenceOptimizer> step_optimizer_;

public:
    HumanoidPathPlanner(const HumanoidConstraints& constraints);
    PathPlan PlanPathWithConstraints(const Pose& start,
                                   const Pose& goal,
                                   const GridMap& traversability_map);
    bool IsStepValid(const Step& step) const;
    bool IsPathStable(const PathPlan& path) const;
    PathPlan OptimizeForHumanoid(const PathPlan& raw_path) const;
};
```

## Advanced Path Planning Algorithms

### 1. Footstep-Aware A* (FA-A*)

```cpp
#include <queue>
#include <vector>
#include <cmath>
#include <algorithm>

struct FootstepNode {
    int x, y;  // Grid coordinates
    double theta;  // Orientation
    double g_cost;  // Cost from start
    double h_cost;  // Heuristic to goal
    double f_cost;  // Total cost (g + h)
    FootstepNode* parent;

    // Humanoid-specific properties
    double balance_score;  // Stability measure
    double step_effort;    // Energy cost of this step

    bool operator>(const FootstepNode& other) const {
        return f_cost > other.f_cost;
    }
};

class FootstepAStar {
private:
    HumanoidConstraints constraints_;
    GridMap traversability_map_;

    // Step validity checking
    bool IsTraversable(const Point2D& pos) const;
    bool IsStableSupport(const Point2D& pos, double orientation) const;
    double CalculateStepCost(const Point2D& from, const Point2D& to, double orientation) const;

    // Heuristic functions
    double CalculateHeuristic(const Point2D& current, const Point2D& goal) const;
    double CalculateOrientationCost(double current_theta, double target_theta) const;

public:
    FootstepAStar(const HumanoidConstraints& constraints);

    std::vector<Footstep> PlanFootsteps(const Pose& start, const Pose& goal);

private:
    std::vector<Footstep> ReconstructPath(FootstepNode* goal_node) const;
    std::vector<FootstepNode> GetNeighbors(const FootstepNode& current) const;
    double CalculateBalanceScore(const Point2D& left_foot,
                               const Point2D& right_foot,
                               const Point2D& com_pos) const;
};

std::vector<Footstep> FootstepAStar::PlanFootsteps(const Pose& start, const Pose& goal) {
    // Initialize open and closed sets
    std::priority_queue<FootstepNode, std::vector<FootstepNode>, std::greater<FootstepNode>> open_set;
    std::vector<std::vector<std::vector<bool>>> closed_set(  // 3D: x, y, theta_discretized
        traversability_map_.GetWidth(),
        std::vector<std::vector<bool>>(
            traversability_map_.GetHeight(),
            std::vector<bool>(32, false)  // Discretized theta (0-2π in 32 steps)
        )
    );

    // Initialize start node
    FootstepNode start_node;
    start_node.x = static_cast<int>(start.position.x / traversability_map_.GetResolution());
    start_node.y = static_cast<int>(start.position.y / traversability_map_.GetResolution());
    start_node.theta = start.orientation;
    start_node.g_cost = 0.0;
    start_node.h_cost = CalculateHeuristic({start_node.x, start_node.y},
                                          {goal.position.x, goal.position.y});
    start_node.f_cost = start_node.g_cost + start_node.h_cost;
    start_node.parent = nullptr;
    start_node.balance_score = 1.0;  // Perfect balance initially
    start_node.step_effort = 0.0;

    open_set.push(start_node);

    while (!open_set.empty()) {
        FootstepNode current = open_set.top();
        open_set.pop();

        // Check if we reached the goal
        Point2D current_pos = {current.x * traversability_map_.GetResolution(),
                               current.y * traversability_map_.GetResolution()};
        if (Distance(current_pos, {goal.position.x, goal.position.y}) < 0.5) {  // 50cm tolerance
            return ReconstructPath(&current);
        }

        // Mark as visited
        int theta_idx = static_cast<int>((current.theta / (2 * M_PI)) * 32) % 32;
        closed_set[current.x][current.y][theta_idx] = true;

        // Explore neighbors
        std::vector<FootstepNode> neighbors = GetNeighbors(current);
        for (auto& neighbor : neighbors) {
            int n_theta_idx = static_cast<int>((neighbor.theta / (2 * M_PI)) * 32) % 32;

            if (closed_set[neighbor.x][neighbor.y][n_theta_idx]) {
                continue;
            }

            // Calculate step validity and cost
            if (!IsTraversable({neighbor.x, neighbor.y}) ||
                !IsStableSupport({neighbor.x, neighbor.y}, neighbor.theta)) {
                continue;
            }

            double step_cost = CalculateStepCost({current.x, current.y},
                                               {neighbor.x, neighbor.y},
                                               current.theta);
            double tentative_g = current.g_cost + step_cost;

            neighbor.g_cost = tentative_g;
            neighbor.h_cost = CalculateHeuristic({neighbor.x, neighbor.y},
                                                {goal.position.x, goal.position.y});
            neighbor.f_cost = neighbor.g_cost + neighbor.h_cost;
            neighbor.parent = &current;

            open_set.push(neighbor);
        }
    }

    // No path found
    return {};
}

std::vector<FootstepNode> FootstepAStar::GetNeighbors(const FootstepNode& current) const {
    std::vector<FootstepNode> neighbors;

    // Generate possible footsteps based on humanoid constraints
    for (double dx = -constraints_.max_step_length; dx <= constraints_.max_step_length; dx += 0.1) {
        for (double dy = -constraints_.max_step_width; dy <= constraints_.max_step_width; dy += 0.1) {
            for (double dtheta = -constraints_.step_turn_angle; dtheta <= constraints_.step_turn_angle; dtheta += 0.1) {

                if (dx == 0 && dy == 0 && dtheta == 0) continue;  // Skip staying in place

                // Check if step is within constraints
                double step_distance = std::sqrt(dx*dx + dy*dy);
                if (step_distance > constraints_.max_step_length) continue;

                FootstepNode neighbor;
                neighbor.x = current.x + static_cast<int>(dx / traversability_map_.GetResolution());
                neighbor.y = current.y + static_cast<int>(dy / traversability_map_.GetResolution());
                neighbor.theta = current.theta + dtheta;

                // Normalize theta to [0, 2π]
                while (neighbor.theta < 0) neighbor.theta += 2 * M_PI;
                while (neighbor.theta >= 2 * M_PI) neighbor.theta -= 2 * M_PI;

                // Check bounds
                if (neighbor.x < 0 || neighbor.x >= traversability_map_.GetWidth() ||
                    neighbor.y < 0 || neighbor.y >= traversability_map_.GetHeight()) {
                    continue;
                }

                neighbors.push_back(neighbor);
            }
        }
    }

    return neighbors;
}
```

### 2. Sampling-Based Humanoid RRT (HRRT)

```cpp
// Humanoid-aware RRT for complex navigation
class HRRTPlanner {
private:
    struct HRRTNode {
        Pose pose;
        HRRTNode* parent;
        std::vector<Step> path_to_parent;  // Steps to reach this node
        double cost;
    };

    HumanoidConstraints constraints_;
    GridMap traversability_map_;
    std::vector<HRRTNode> tree_nodes_;
    std::mt19937 rng_;

    // RRT parameters
    double step_size_ = 0.2;
    double goal_bias_ = 0.05;
    int max_iterations_ = 10000;
    double goal_tolerance_ = 0.3;

public:
    HRRTPlanner(const HumanoidConstraints& constraints);
    PathPlan PlanPath(const Pose& start, const Pose& goal);

private:
    Pose SampleFreeSpace(const Pose& goal) const;
    HRRTNode* GetNearestNode(const Pose& target) const;
    bool ExtendTree(const Pose& sample, HRRTNode& nearest);
    bool IsValidExtension(const HRRTNode& from, const Pose& to) const;
    std::vector<Step> GenerateStepsBetween(const Pose& from, const Pose& to) const;
    PathPlan ExtractPath(HRRTNode* goal_node) const;
};

PathPlan HRRTPlanner::PlanPath(const Pose& start, const Pose& goal) {
    // Initialize tree with start node
    HRRTNode start_node;
    start_node.pose = start;
    start_node.parent = nullptr;
    start_node.cost = 0.0;
    tree_nodes_.clear();
    tree_nodes_.push_back(start_node);

    for (int iter = 0; iter < max_iterations_; ++iter) {
        // Sample target (with goal bias)
        Pose sample;
        if (static_cast<double>(rng_()) / rng_.max() < goal_bias_) {
            sample = goal;  // Bias toward goal
        } else {
            sample = SampleFreeSpace(goal);
        }

        // Find nearest node in tree
        HRRTNode* nearest = GetNearestNode(sample);

        // Try to extend tree toward sample
        if (ExtendTree(sample, *nearest)) {
            HRRTNode& new_node = tree_nodes_.back();

            // Check if we're near the goal
            if (Distance(new_node.pose.position, goal.position) < goal_tolerance_) {
                return ExtractPath(&new_node);
            }
        }
    }

    // Failed to find path
    return PathPlan();
}

bool HRRTPlanner::ExtendTree(const Pose& sample, HRRTNode& nearest) {
    // Calculate direction vector
    Vector2D direction = {
        sample.position.x - nearest.pose.position.x,
        sample.position.y - nearest.pose.position.y
    };

    double distance = std::sqrt(direction.x * direction.x + direction.y * direction.y);

    // Normalize and scale to step size
    if (distance > step_size_) {
        direction.x = (direction.x / distance) * step_size_;
        direction.y = (direction.y / distance) * step_size_;
    }

    // Calculate new pose
    Pose new_pose;
    new_pose.position.x = nearest.pose.position.x + direction.x;
    new_pose.position.y = nearest.pose.position.y + direction.y;

    // Interpolate orientation
    double angle_diff = sample.orientation - nearest.pose.orientation;
    // Normalize angle difference to [-π, π]
    while (angle_diff > M_PI) angle_diff -= 2 * M_PI;
    while (angle_diff < -M_PI) angle_diff += 2 * M_PI;

    new_pose.orientation = nearest.pose.orientation +
                          std::clamp(angle_diff, -constraints_.step_turn_angle,
                                    constraints_.step_turn_angle);

    // Check validity of extension
    if (!IsValidExtension(nearest, new_pose)) {
        return false;
    }

    // Generate steps between nearest and new pose
    std::vector<Step> steps = GenerateStepsBetween(nearest.pose, new_pose);

    // Create new node
    HRRTNode new_node;
    new_node.pose = new_pose;
    new_node.parent = &nearest;
    new_node.path_to_parent = steps;
    new_node.cost = nearest.cost + CalculatePathCost(steps);

    tree_nodes_.push_back(new_node);
    return true;
}

std::vector<Step> HRRTPlanner::GenerateStepsBetween(const Pose& from, const Pose& to) const {
    std::vector<Step> steps;

    // Calculate required steps based on step size
    Vector2D displacement = {
        to.position.x - from.position.x,
        to.position.y - from.position.y
    };

    double total_distance = std::sqrt(displacement.x * displacement.x +
                                     displacement.y * displacement.y);

    int num_steps = std::ceil(total_distance / constraints_.min_step_length);

    for (int i = 1; i <= num_steps; ++i) {
        double fraction = static_cast<double>(i) / num_steps;

        Step step;
        step.position.x = from.position.x + displacement.x * fraction;
        step.position.y = from.position.y + displacement.y * fraction;

        // Interpolate orientation
        double angle_diff = to.orientation - from.orientation;
        while (angle_diff > M_PI) angle_diff -= 2 * M_PI;
        while (angle_diff < -M_PI) angle_diff += 2 * M_PI;

        step.orientation = from.orientation + angle_diff * fraction;

        steps.push_back(step);
    }

    return steps;
}
```

### 3. Humanoid Trajectory Optimizer

```cpp
// Trajectory optimization for smooth humanoid motion
class HumanoidTrajectoryOptimizer {
private:
    HumanoidConstraints constraints_;

    // Optimization parameters
    double smoothness_weight_ = 0.5;
    double obstacle_weight_ = 2.0;
    double balance_weight_ = 1.0;
    double energy_weight_ = 0.3;

public:
    HumanoidTrajectoryOptimizer(const HumanoidConstraints& constraints);

    Trajectory OptimizeTrajectory(const PathPlan& raw_path,
                                 const GridMap& traversability_map) const;

private:
    Trajectory SmoothPath(const std::vector<Pose>& waypoints) const;
    double CalculateObstacleCost(const Pose& pose, const GridMap& map) const;
    double CalculateBalanceCost(const Pose& pose) const;
    double CalculateEnergyCost(const std::vector<Pose>& path) const;
    std::vector<Pose> OptimizeWaypoints(const std::vector<Pose>& waypoints,
                                       const GridMap& map) const;
};

Trajectory HumanoidTrajectoryOptimizer::OptimizeTrajectory(
    const PathPlan& raw_path,
    const GridMap& traversability_map) const {

    // Convert path plan to waypoints
    std::vector<Pose> waypoints = raw_path.GetWaypoints();

    // Optimize waypoints considering humanoid constraints
    std::vector<Pose> optimized_waypoints = OptimizeWaypoints(waypoints, traversability_map);

    // Generate smooth trajectory between waypoints
    Trajectory trajectory = SmoothPath(optimized_waypoints);

    return trajectory;
}

std::vector<Pose> HumanoidTrajectoryOptimizer::OptimizeWaypoints(
    const std::vector<Pose>& waypoints,
    const GridMap& map) const {

    if (waypoints.size() < 3) return waypoints;  // Nothing to optimize

    std::vector<Pose> optimized = waypoints;

    // Iterative optimization
    for (int iter = 0; iter < 50; ++iter) {  // Max 50 iterations
        bool improved = false;

        for (size_t i = 1; i < optimized.size() - 1; ++i) {
            Pose original_point = optimized[i];

            // Try perturbing the point
            for (double dx = -0.1; dx <= 0.1; dx += 0.05) {
                for (double dy = -0.1; dy <= 0.1; dy += 0.05) {
                    Pose perturbed = optimized[i];
                    perturbed.position.x += dx;
                    perturbed.position.y += dy;

                    // Calculate cost of perturbed path
                    std::vector<Pose> test_path = optimized;
                    test_path[i] = perturbed;

                    double original_cost = CalculateTotalCost(optimized, map);
                    double perturbed_cost = CalculateTotalCost(test_path, map);

                    if (perturbed_cost < original_cost) {
                        optimized[i] = perturbed;
                        improved = true;
                    }
                }
            }
        }

        if (!improved) break;  // Converged
    }

    return optimized;
}

double HumanoidTrajectoryOptimizer::CalculateTotalCost(
    const std::vector<Pose>& path,
    const GridMap& map) const {

    double total_cost = 0.0;

    for (size_t i = 0; i < path.size(); ++i) {
        // Obstacle cost
        total_cost += obstacle_weight_ * CalculateObstacleCost(path[i], map);

        // Balance cost
        total_cost += balance_weight_ * CalculateBalanceCost(path[i]);

        // Smoothness cost (penalize sharp turns)
        if (i > 0) {
            double dist = Distance(path[i-1].position, path[i].position);
            double angle_change = std::abs(path[i].orientation - path[i-1].orientation);
            total_cost += smoothness_weight_ * (dist + angle_change);
        }
    }

    // Energy cost for the entire path
    total_cost += energy_weight_ * CalculateEnergyCost(path);

    return total_cost;
}

Trajectory HumanoidTrajectoryOptimizer::SmoothPath(const std::vector<Pose>& waypoints) const {
    Trajectory trajectory;

    if (waypoints.size() < 2) return trajectory;

    // Use cubic spline interpolation for smooth path
    for (size_t i = 0; i < waypoints.size() - 1; ++i) {
        // Generate intermediate poses between waypoints
        std::vector<Pose> segment = GenerateSplineSegment(waypoints[i], waypoints[i+1]);
        trajectory.AddSegment(segment);
    }

    return trajectory;
}

std::vector<Pose> HumanoidTrajectoryOptimizer::GenerateSplineSegment(
    const Pose& start, const Pose& end) const {

    std::vector<Pose> segment;

    // Calculate intermediate poses using cubic spline
    int num_intermediate = static_cast<int>(Distance(start.position, end.position) / 0.05);  // 5cm resolution

    for (int i = 1; i < num_intermediate; ++i) {
        double t = static_cast<double>(i) / num_intermediate;

        // Cubic spline interpolation
        double x = (2*t*t*t - 3*t*t + 1) * start.position.x +
                   (t*t*t - 2*t*t + t) * constraints_.max_linear_vel * std::cos(start.orientation) +
                   (-2*t*t*t + 3*t*t) * end.position.x +
                   (t*t*t - t*t) * constraints_.max_linear_vel * std::cos(end.orientation);

        double y = (2*t*t*t - 3*t*t + 1) * start.position.y +
                   (t*t*t - 2*t*t + t) * constraints_.max_linear_vel * std::sin(start.orientation) +
                   (-2*t*t*t + 3*t*t) * end.position.y +
                   (t*t*t - t*t) * constraints_.max_linear_vel * std::sin(end.orientation);

        // Interpolate orientation
        double angle_diff = end.orientation - start.orientation;
        while (angle_diff > M_PI) angle_diff -= 2 * M_PI;
        while (angle_diff < -M_PI) angle_diff += 2 * M_PI;

        double theta = start.orientation + t * angle_diff;

        Pose intermediate;
        intermediate.position = {x, y};
        intermediate.orientation = theta;

        segment.push_back(intermediate);
    }

    return segment;
}
```

## Semantic Path Planning

### Integrating Object and Scene Understanding

```cpp
// Semantic path planning considering object affordances and scene understanding
struct SemanticConstraint {
    std::string object_type;      // "chair", "table", "door", etc.
    std::vector<Affordance> affordances;  // "sit_on", "navigate_around", "grasp", etc.
    double importance_weight;     // How much to consider this object
    bool avoid_object;           // Whether to avoid this object
    bool use_for_guidance;       // Whether to use for path guidance
};

class SemanticPathPlanner {
private:
    std::vector<SemanticConstraint> semantic_constraints_;
    SceneGraph scene_graph_;

public:
    SemanticPathPlanner();
    PathPlan PlanPathWithSemantics(const Pose& start,
                                  const Pose& goal,
                                  const SceneGraph& scene,
                                  const std::vector<SemanticConstraint>& constraints);

private:
    double CalculateSemanticCost(const Pose& pose,
                                const SceneGraph& scene,
                                const std::vector<SemanticConstraint>& constraints) const;
    std::vector<Pose> FilterPathBySemantics(const std::vector<Pose>& raw_path,
                                           const SceneGraph& scene,
                                           const std::vector<SemanticConstraint>& constraints) const;
    void UpdateSceneGraphWithDynamicObjects(SceneGraph& scene,
                                          const std::vector<DetectedObject>& dynamic_objects) const;
};

PathPlan SemanticPathPlanner::PlanPathWithSemantics(
    const Pose& start,
    const Pose& goal,
    const SceneGraph& scene,
    const std::vector<SemanticConstraint>& constraints) {

    // First, plan a basic path using conventional methods
    HumanoidPathPlanner basic_planner(constraints_[0].humanoid_constraints);  // Get basic constraints
    PathPlan basic_path = basic_planner.PlanPathWithConstraints(start, goal, scene.GetTraversabilityMap());

    if (basic_path.IsEmpty()) {
        return PathPlan();  // No basic path found
    }

    // Then, enhance with semantic considerations
    std::vector<Pose> enhanced_waypoints =
        FilterPathBySemantics(basic_path.GetWaypoints(), scene, constraints);

    // Recalculate trajectory with semantic costs
    HumanoidTrajectoryOptimizer optimizer(constraints_[0].humanoid_constraints);
    Trajectory optimized_trajectory =
        optimizer.OptimizeTrajectory(enhanced_waypoints, scene.GetTraversabilityMap());

    // Create final path plan with semantic annotations
    PathPlan semantic_path;
    semantic_path.SetWaypoints(enhanced_waypoints);
    semantic_path.SetTrajectory(optimized_trajectory);
    semantic_path.SetSemanticAnnotations(AnnotatePathWithSemantics(enhanced_waypoints, scene));

    return semantic_path;
}

std::vector<Pose> SemanticPathPlanner::FilterPathBySemantics(
    const std::vector<Pose>& raw_path,
    const SceneGraph& scene,
    const std::vector<SemanticConstraint>& constraints) const {

    std::vector<Pose> filtered_path;

    for (const auto& pose : raw_path) {
        // Calculate semantic cost for this pose
        double semantic_cost = CalculateSemanticCost(pose, scene, constraints);

        // If cost is too high, try to find an alternative nearby pose
        if (semantic_cost > semantic_threshold_) {
            Pose adjusted_pose = FindSemanticallyBetterPose(pose, scene, constraints);
            filtered_path.push_back(adjusted_pose);
        } else {
            filtered_path.push_back(pose);
        }
    }

    return filtered_path;
}

double SemanticPathPlanner::CalculateSemanticCost(
    const Pose& pose,
    const SceneGraph& scene,
    const std::vector<SemanticConstraint>& constraints) const {

    double total_cost = 0.0;

    // Check for nearby semantic objects
    auto nearby_objects = scene.GetNearbyObjects(pose.position, 2.0);  // 2m radius

    for (const auto& obj : nearby_objects) {
        auto constraint_it = std::find_if(constraints.begin(), constraints.end(),
            [&obj](const SemanticConstraint& sc) {
                return sc.object_type == obj.GetType();
            });

        if (constraint_it != constraints.end()) {
            const auto& constraint = *constraint_it;

            // Calculate distance-based cost
            double distance = Distance(pose.position, obj.GetPosition());

            if (constraint.avoid_object) {
                // Exponentially increase cost as we get closer to avoided objects
                double avoidance_cost = constraint.importance_weight *
                                       std::exp(-distance / 0.5);  // Falloff at 0.5m
                total_cost += avoidance_cost;
            }

            if (constraint.use_for_guidance) {
                // Prefer paths near objects that can be used for guidance
                double guidance_benefit = -constraint.importance_weight *
                                         std::exp(-std::abs(distance - 1.0) / 0.5);  // Optimal at 1m
                total_cost += guidance_benefit;
            }
        }
    }

    return total_cost;
}

std::vector<PathAnnotation> SemanticPathPlanner::AnnotatePathWithSemantics(
    const std::vector<Pose>& path,
    const SceneGraph& scene) const {

    std::vector<PathAnnotation> annotations;

    for (size_t i = 0; i < path.size(); ++i) {
        PathAnnotation annotation;
        annotation.path_index = i;
        annotation.position = path[i].position;

        // Find nearby semantic objects
        auto nearby_objects = scene.GetNearbyObjects(path[i].position, 1.0);

        for (const auto& obj : nearby_objects) {
            if (obj.GetDistanceTo(path[i].position) < 0.5) {  // Within 50cm
                SemanticObject semantic_obj;
                semantic_obj.type = obj.GetType();
                semantic_obj.distance = obj.GetDistanceTo(path[i].position);
                semantic_obj.position = obj.GetPosition();
                semantic_obj.affordances = obj.GetAffordances();

                annotation.nearby_objects.push_back(semantic_obj);
            }
        }

        annotations.push_back(annotation);
    }

    return annotations;
}
```

## Dynamic Obstacle Handling

### Real-time Path Replanning

```cpp
// Dynamic obstacle handling and replanning
class DynamicPathManager {
private:
    PathPlan current_path_;
    size_t current_waypoint_index_;
    std::chrono::steady_clock::time_point last_replan_time_;
    double replan_cooldown_;  // Minimum time between replans
    double obstacle_detection_radius_;

    // Path tracking
    PathTracker path_tracker_;

    // Obstacle prediction
    ObstaclePredictor obstacle_predictor_;

public:
    DynamicPathManager(double replan_cooldown = 2.0,  // 2 seconds cooldown
                      double detection_radius = 3.0);  // 3m detection radius

    NavigationResult UpdateWithDynamicObstacles(
        const std::vector<DetectedObject>& detected_objects,
        const Pose& current_pose,
        const Twist& current_velocity);

    bool ShouldReplan(const std::vector<DetectedObject>& detected_objects,
                     const Pose& current_pose) const;

private:
    PathPlan ReplanPath(const Pose& start,
                       const Pose& goal,
                       const std::vector<DetectedObject>& dynamic_obstacles) const;
    std::vector<Pose> PredictObstacleTrajectories(
        const std::vector<DetectedObject>& obstacles) const;
    bool IsPathBlocked(const PathPlan& path,
                      const std::vector<DetectedObject>& obstacles,
                      size_t start_index) const;
    double CalculateRisk(const Pose& pose,
                        const std::vector<DetectedObject>& obstacles) const;
};

NavigationResult DynamicPathManager::UpdateWithDynamicObstacles(
    const std::vector<DetectedObject>& detected_objects,
    const Pose& current_pose,
    const Twist& current_velocity) {

    NavigationResult result;

    // Check if we need to replan
    bool need_replan = ShouldReplan(detected_objects, current_pose);

    if (need_replan) {
        // Get the ultimate goal (from original plan or new command)
        Pose goal = current_path_.GetGoal();

        // Replan from current position
        PathPlan new_path = ReplanPath(current_pose, goal, detected_objects);

        if (!new_path.IsEmpty()) {
            current_path_ = new_path;
            current_waypoint_index_ = 0;  // Start from beginning of new path
            last_replan_time_ = std::chrono::steady_clock::now();

            result.status = NavigationStatus::REPLANNED;
            result.message = "Path replanned due to dynamic obstacles";
        } else {
            result.status = NavigationStatus::NO_PATH_FOUND;
            result.message = "Could not find path around dynamic obstacles";
            return result;
        }
    }

    // Continue with path following
    PathSegment next_segment = current_path_.GetSegment(current_waypoint_index_);

    // Use path tracker to generate velocity commands
    Twist cmd_vel = path_tracker_.CalculateVelocityCommand(
        current_pose, current_velocity, next_segment);

    result.command = cmd_vel;
    result.status = NavigationStatus::IN_PROGRESS;
    result.remaining_path = current_path_.GetRemainingPath(current_waypoint_index_);

    return result;
}

bool DynamicPathManager::ShouldReplan(
    const std::vector<DetectedObject>& detected_objects,
    const Pose& current_pose) const {

    // Check if enough time has passed since last replan
    auto now = std::chrono::steady_clock::now();
    auto time_since_replan = std::chrono::duration<double>(now - last_replan_time_).count();

    if (time_since_replan < replan_cooldown_) {
        return false;  // Respect cooldown period
    }

    // Check for imminent collision risk
    for (const auto& obj : detected_objects) {
        if (obj.IsMoving() && obj.GetClass() != "person") {  // Focus on moving non-person objects
            double distance = Distance(current_pose.position, obj.GetPosition());

            // Predict collision based on object velocity and robot velocity
            if (distance < obstacle_detection_radius_ / 2.0) {  // Within half radius
                double time_to_collision = PredictCollisionTime(
                    current_pose, current_velocity, obj);

                if (time_to_collision < 3.0) {  // Less than 3 seconds to collision
                    return true;
                }
            }
        }
    }

    // Check if current path is blocked
    if (IsPathBlocked(current_path_, detected_objects, current_waypoint_index_)) {
        return true;
    }

    return false;
}

PathPlan DynamicPathManager::ReplanPath(
    const Pose& start,
    const Pose& goal,
    const std::vector<DetectedObject>& dynamic_obstacles) const {

    // Create a temporary map with predicted obstacle positions
    GridMap temporary_map = GetBaseTraversabilityMap();

    // Add predicted obstacle positions to the map
    auto predicted_obstacles = PredictObstacleTrajectories(dynamic_obstacles);

    for (const auto& obs : predicted_obstacles) {
        // Mark obstacle in map with temporal consideration
        temporary_map.MarkObstacle(obs.position, 0.5, 2.0);  // 50cm radius, 2m height
    }

    // Plan path with updated map
    HumanoidPathPlanner planner(GetHumanoidConstraints());
    PathPlan new_path = planner.PlanPathWithConstraints(start, goal, temporary_map);

    return new_path;
}

std::vector<Pose> DynamicPathManager::PredictObstacleTrajectories(
    const std::vector<DetectedObject>& obstacles) const {

    std::vector<Pose> predicted_positions;
    double prediction_horizon = 5.0;  // Predict 5 seconds ahead
    double time_step = 0.5;  // 500ms intervals

    for (const auto& obj : obstacles) {
        if (!obj.IsMoving()) continue;

        // Extrapolate position based on velocity
        Pose current_pos = obj.GetPose();
        Twist velocity = obj.GetVelocity();

        for (double t = time_step; t <= prediction_horizon; t += time_step) {
            Pose future_pos;
            future_pos.position.x = current_pos.position.x + velocity.linear.x * t;
            future_pos.position.y = current_pos.position.y + velocity.linear.y * t;
            future_pos.orientation = current_pos.orientation + velocity.angular.z * t;

            predicted_positions.push_back(future_pos);
        }
    }

    return predicted_positions;
}
```

## Integration with VLA Systems

### Vision-Language-Action Navigation

```cpp
// Integration with Vision-Language-Action systems
class VLANavigationManager {
private:
    std::unique_ptr<SemanticPathPlanner> semantic_planner_;
    std::unique_ptr<DynamicPathManager> dynamic_manager_;
    std::unique_ptr<HumanoidTrajectoryOptimizer> optimizer_;

    // Natural language interface
    std::unique_ptr<NaturalLanguageNavigator> nl_navigator_;

    // Scene understanding
    std::unique_ptr<SceneUnderstandingSystem> scene_understanding_;

public:
    VLANavigationManager();

    NavigationResult ProcessNavigationCommand(
        const std::string& command,
        const SceneGraph& current_scene,
        const Pose& current_pose);

    PathPlan PlanSemanticPath(const NLCommand& parsed_command,
                             const SceneGraph& scene,
                             const Pose& start,
                             const Pose& goal);

private:
    NLCommand ParseNavigationCommand(const std::string& command);
    std::vector<SemanticConstraint> ExtractSemanticConstraints(
        const NLCommand& command,
        const SceneGraph& scene) const;
    bool ValidateNavigationFeasibility(const NLCommand& command,
                                     const SceneGraph& scene) const;
    NavigationResult ExecuteNavigationWithFeedback(
        const PathPlan& path_plan,
        const std::string& command);
};

NavigationResult VLANavigationManager::ProcessNavigationCommand(
    const std::string& command,
    const SceneGraph& current_scene,
    const Pose& current_pose) {

    // Parse natural language command
    NLCommand nl_command = ParseNavigationCommand(command);

    if (nl_command.type == NLCommandType::INVALID) {
        return NavigationResult{NavigationStatus::INVALID_COMMAND, "Could not understand navigation command"};
    }

    // Validate command feasibility
    if (!ValidateNavigationFeasibility(nl_command, current_scene)) {
        return NavigationResult{NavigationStatus::UNREACHABLE_GOAL, "Navigation goal is not reachable"};
    }

    // Extract goal from command
    Pose goal_pose = nl_navigator_->ExtractGoalPose(nl_command, current_scene, current_pose);

    if (!goal_pose.IsValid()) {
        return NavigationResult{NavigationStatus::INVALID_GOAL, "Could not determine valid goal pose"};
    }

    // Extract semantic constraints from command
    std::vector<SemanticConstraint> semantic_constraints =
        ExtractSemanticConstraints(nl_command, current_scene);

    // Plan path with semantics
    PathPlan path_plan = PlanSemanticPath(nl_command, current_scene, current_pose, goal_pose);

    if (path_plan.IsEmpty()) {
        return NavigationResult{NavigationStatus::NO_PATH_FOUND, "Could not find valid path"};
    }

    // Execute navigation with feedback
    return ExecuteNavigationWithFeedback(path_plan, command);
}

std::vector<SemanticConstraint> VLANavigationManager::ExtractSemanticConstraints(
    const NLCommand& command,
    const SceneGraph& scene) const {

    std::vector<SemanticConstraint> constraints;

    // Add constraints based on command type
    switch (command.type) {
        case NLCommandType::NAVIGATE_TO_OBJECT:
            {
                SemanticConstraint obj_constraint;
                obj_constraint.object_type = command.target_object;
                obj_constraint.avoid_object = false;
                obj_constraint.use_for_guidance = true;
                obj_constraint.importance_weight = 2.0;
                constraints.push_back(obj_constraint);

                // Also add constraints for related objects (e.g., avoid fragile items near target)
                auto related_objects = scene.GetRelatedObjects(command.target_object);
                for (const auto& related_obj : related_objects) {
                    if (related_obj.IsFragile()) {
                        SemanticConstraint fragile_constraint;
                        fragile_constraint.object_type = related_obj.GetType();
                        fragile_constraint.avoid_object = true;
                        fragile_constraint.use_for_guidance = false;
                        fragile_constraint.importance_weight = 3.0;
                        constraints.push_back(fragile_constraint);
                    }
                }
            }
            break;

        case NLCommandType::NAVIGATE_AVOID_OBJECT:
            {
                SemanticConstraint avoid_constraint;
                avoid_constraint.object_type = command.target_object;
                avoid_constraint.avoid_object = true;
                avoid_constraint.use_for_guidance = false;
                avoid_constraint.importance_weight = 5.0;  // High importance for avoidance
                constraints.push_back(avoid_constraint);
            }
            break;

        case NLCommandType::NAVIGATE_THROUGH_AREA:
            {
                // Add constraints for doorway/passageway navigation
                auto passageways = scene.GetPassageways(command.target_area);
                for (const auto& pw : passageways) {
                    SemanticConstraint pw_constraint;
                    pw_constraint.object_type = "passageway";
                    pw_constraint.avoid_object = false;
                    pw_constraint.use_for_guidance = true;
                    pw_constraint.importance_weight = 1.5;
                    constraints.push_back(pw_constraint);
                }
            }
            break;

        default:
            // Add general humanoid constraints
            SemanticConstraint general_constraint;
            general_constraint.object_type = "obstacle";
            general_constraint.avoid_object = true;
            general_constraint.use_for_guidance = false;
            general_constraint.importance_weight = 1.0;
            constraints.push_back(general_constraint);
            break;
    }

    return constraints;
}

NavigationResult VLANavigationManager::ExecuteNavigationWithFeedback(
    const PathPlan& path_plan,
    const std::string& command) {

    NavigationResult result;
    result.status = NavigationStatus::IN_PROGRESS;

    // Provide feedback to user about the plan
    std::string feedback = GenerateNavigationFeedback(path_plan, command);

    // Start execution
    auto execution_result = ExecutePath(path_plan);

    // Update result based on execution
    result.status = execution_result.status;
    result.message = execution_result.message;

    if (execution_result.status == NavigationStatus::SUCCESS) {
        result.message = "Successfully navigated to destination. " + feedback;
    } else if (execution_result.status == NavigationStatus::REPLANNED) {
        result.message = "Had to replan path due to obstacles. " + feedback;
    }

    return result;
}

std::string VLANavigationManager::GenerateNavigationFeedback(
    const PathPlan& path_plan,
    const std::string& command) const {

    // Generate natural language feedback about the navigation plan
    std::ostringstream feedback;

    auto annotations = path_plan.GetSemanticAnnotations();
    if (!annotations.empty()) {
        feedback << "I will navigate by ";

        // Mention key objects along the path
        std::set<std::string> mentioned_objects;
        for (const auto& annotation : annotations) {
            for (const auto& obj : annotation.nearby_objects) {
                if (mentioned_objects.size() < 3 &&  // Limit to 3 objects
                    obj.distance < 1.0 &&  // Within 1m
                    mentioned_objects.insert(obj.type).second) {  // Newly inserted
                    feedback << "passing " << obj.type << ", ";
                }
            }
        }

        feedback << "to reach the destination.";
    } else {
        feedback << "following the planned path to your destination.";
    }

    return feedback.str();
}
```

This comprehensive path planning system provides the foundation for intelligent navigation in humanoid robots, incorporating kinematic constraints, semantic understanding, and dynamic obstacle handling essential for vision-language-action systems.