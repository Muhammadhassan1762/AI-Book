---
sidebar_position: 3
---

# Navigation Behaviors and Actions

## Implementing Humanoid Navigation Behaviors with ROS 2 Actions

Navigation behaviors in humanoid robots require sophisticated action management to handle complex, multi-step navigation tasks. This chapter covers the implementation of navigation behaviors using ROS 2 actions, behavior trees, and humanoid-specific movement patterns for vision-language-action systems.

## Learning Objectives

By the end of this chapter, you will:
- Understand ROS 2 actions for navigation tasks
- Implement humanoid-specific navigation behaviors
- Design behavior trees for complex navigation scenarios
- Create recovery behaviors for navigation failures
- Integrate navigation with vision-language systems
- Handle dynamic environments and human-aware navigation
- Implement safe navigation for humanoid platforms

## ROS 2 Actions for Navigation

### Navigation Action Architecture

```cpp
// navigation_actions.cpp
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <nav2_msgs/action/navigate_to_pose.hpp>
#include <nav2_msgs/action/navigate_through_poses.hpp>
#include <nav2_msgs/action/compute_path_to_pose.hpp>
#include <nav2_msgs/action/follow_path.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>

using NavigateToPose = nav2_msgs::action::NavigateToPose;
using NavigateThroughPoses = nav2_msgs::action::NavigateThroughPoses;
using ComputePathToPose = nav2_msgs::action::ComputePathToPose;
using FollowPath = nav2_msgs::action::FollowPath;

class HumanoidNavigateToPoseAction : public rclcpp::Node
{
public:
    using GoalHandleNavigateToPose = rclcpp_action::ServerGoalHandle<NavigateToPose>;

    explicit HumanoidNavigateToPoseAction(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
    : Node("humanoid_navigate_to_pose_action_server", options)
    {
        // Initialize action server
        this->action_server_ = rclcpp_action::create_server<NavigateToPose>(
            this->get_node_base_interface(),
            this->get_node_clock_interface(),
            this->get_node_logging_interface(),
            this->get_node_waitables_interface(),
            "navigate_to_pose",
            std::bind(&HumanoidNavigateToPoseAction::handle_goal, this, std::placeholders::_1, std::placeholders::_2),
            std::bind(&HumanoidNavigateToPoseAction::handle_cancel, this, std::placeholders::_1),
            std::bind(&HumanoidNavigateToPoseAction::handle_accepted, this, std::placeholders::_1));

        // Initialize navigation components
        this->path_planner_ = std::make_unique<HumanoidPathPlanner>();
        this->path_follower_ = std::make_unique<HumanoidPathFollower>();
        this->recovery_manager_ = std::make_unique<RecoveryManager>();

        // Initialize TF listener
        this->tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
        this->tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

        RCLCPP_INFO(this->get_logger(), "Humanoid Navigate To Pose Action Server initialized");
    }

private:
    rclcpp_action::Server<NavigateToPose>::SharedPtr action_server_;
    std::unique_ptr<HumanoidPathPlanner> path_planner_;
    std::unique_ptr<HumanoidPathFollower> path_follower_;
    std::unique_ptr<RecoveryManager> recovery_manager_;
    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

    // Navigation state
    bool is_navigating_{false};
    rclcpp::Time navigation_start_time_;
    geometry_msgs::msg::PoseStamped current_goal_;

    // Action callbacks
    rclcpp_action::GoalResponse handle_goal(
        const rclcpp_action::GoalUUID & uuid,
        std::shared_ptr<const NavigateToPose::Goal> goal)
    {
        RCLCPP_INFO(this->get_logger(), "Received navigation goal");

        if (is_navigating_) {
            RCLCPP_WARN(this->get_logger(), "Already navigating, rejecting new goal");
            return rclcpp_action::GoalResponse::REJECT;
        }

        // Validate goal pose
        if (!isValidGoal(goal->pose)) {
            RCLCPP_ERROR(this->get_logger(), "Invalid goal pose");
            return rclcpp_action::GoalResponse::REJECT;
        }

        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    rclcpp_action::CancelResponse handle_cancel(
        const std::shared_ptr<GoalHandleNavigateToPose> goal_handle)
    {
        RCLCPP_INFO(this->get_logger(), "Received request to cancel navigation goal");

        // Stop current navigation
        path_follower_->stop();

        return rclcpp_action::CancelResponse::ACCEPT;
    }

    void handle_accepted(const std::shared_ptr<GoalHandleNavigateToPose> goal_handle)
    {
        // This needs to be called from a separate thread
        using namespace std::placeholders;

        std::thread{std::bind(&HumanoidNavigateToPoseAction::execute, this, _1), goal_handle}.detach();
    }

    void execute(const std::shared_ptr<GoalHandleNavigateToPose> goal_handle)
    {
        RCLCPP_INFO(this->get_logger(), "Executing navigation goal");

        // Set navigation state
        is_navigating_ = true;
        navigation_start_time_ = this->get_clock()->now();
        current_goal_ = goal_handle->get_goal()->pose;

        // Initialize feedback
        auto feedback = std::make_shared<NavigateToPose::Feedback>();
        auto result = std::make_shared<NavigateToPose::Result>();

        // Get current pose
        geometry_msgs::msg::PoseStamped current_pose;
        if (!getCurrentPose(current_pose)) {
            RCLCPP_ERROR(this->get_logger(), "Failed to get current pose");
            goal_handle->abort(result);
            is_navigating_ = false;
            return;
        }

        // Plan path
        PathPlan path_plan;
        try {
            path_plan = path_planner_->planPath(current_pose.pose, current_goal_.pose);
        } catch (const std::exception& e) {
            RCLCPP_ERROR(this->get_logger(), "Failed to plan path: %s", e.what());
            goal_handle->abort(result);
            is_navigating_ = false;
            return;
        }

        if (path_plan.isEmpty()) {
            RCLCPP_ERROR(this->get_logger(), "No valid path found");
            result->error_code = NavigateToPose::Result::FAILURE;
            result->error_message = "No valid path found";
            goal_handle->succeed(result);
            is_navigating_ = false;
            return;
        }

        // Execute path following
        NavigationStatus status = NavigationStatus::IN_PROGRESS;
        double total_distance = 0.0;
        int recovery_attempts = 0;
        const int max_recovery_attempts = 3;

        while (status == NavigationStatus::IN_PROGRESS && rclcpp::ok()) {
            // Check for cancellation
            if (goal_handle->is_canceling()) {
                path_follower_->stop();
                goal_handle->canceled(result);
                is_navigating_ = false;
                return;
            }

            // Get current pose
            if (!getCurrentPose(current_pose)) {
                RCLCPP_ERROR(this->get_logger(), "Failed to get current pose during navigation");
                status = NavigationStatus::FAILURE;
                continue;
            }

            // Calculate distance traveled
            double distance_traveled = calculateDistance(current_pose.pose, current_start_pose_.pose);
            total_distance = distance_traveled;

            // Update feedback
            feedback->current_pose = current_pose;
            feedback->distance_remaining = calculateDistance(current_pose.pose, current_goal_.pose);
            feedback->distance_traveled = total_distance;
            goal_handle->publish_feedback(feedback);

            // Follow path
            NavigationResult nav_result = path_follower_->followPath(path_plan, current_pose);

            if (nav_result.status == NavigationStatus::SUCCESS) {
                // Check if we're close enough to goal
                double distance_to_goal = calculateDistance(current_pose.pose, current_goal_.pose);
                if (distance_to_goal < goal_tolerance_) {
                    RCLCPP_INFO(this->get_logger(), "Reached goal successfully");
                    status = NavigationStatus::SUCCESS;
                } else {
                    // Continue navigation
                    continue;
                }
            } else if (nav_result.status == NavigationStatus::BLOCKED || nav_result.status == NavigationStatus::STUCK) {
                // Handle navigation failure with recovery
                if (recovery_attempts < max_recovery_attempts) {
                    RCLCPP_WARN(this->get_logger(), "Navigation blocked/stuck, attempting recovery (attempt %d/%d)",
                              recovery_attempts + 1, max_recovery_attempts);

                    RecoveryResult recovery_result = recovery_manager_->executeRecovery(nav_result.failure_reason);
                    if (recovery_result.success) {
                        // Resume navigation after recovery
                        recovery_attempts++;
                        continue;
                    } else {
                        RCLCPP_ERROR(this->get_logger(), "Recovery failed, aborting navigation");
                        status = NavigationStatus::FAILURE;
                    }
                } else {
                    RCLCPP_ERROR(this->get_logger(), "Max recovery attempts reached, aborting navigation");
                    status = NavigationStatus::FAILURE;
                }
            } else if (nav_result.status == NavigationStatus::FAILURE) {
                RCLCPP_ERROR(this->get_logger(), "Navigation failed: %s", nav_result.message.c_str());
                status = NavigationStatus::FAILURE;
            }

            // Small delay to prevent busy waiting
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        // Handle final result
        if (status == NavigationStatus::SUCCESS) {
            result->error_code = NavigateToPose::Result::SUCCESS;
            result->error_message = "Successfully reached goal";
            goal_handle->succeed(result);
            RCLCPP_INFO(this->get_logger(), "Navigation succeeded");
        } else {
            result->error_code = NavigateToPose::Result::FAILURE;
            result->error_message = "Navigation failed";
            goal_handle->abort(result);
            RCLCPP_ERROR(this->get_logger(), "Navigation failed");
        }

        is_navigating_ = false;
    }

    bool isValidGoal(const geometry_msgs::msg::Pose& pose) const {
        // Check if goal is in a valid frame
        try {
            geometry_msgs::msg::PoseStamped stamped_pose;
            stamped_pose.header.frame_id = "map";
            stamped_pose.pose = pose;
            stamped_pose.header.stamp = tf_buffer_->now();

            // Transform to base frame to validate
            geometry_msgs::msg::PoseStamped transformed_pose;
            tf_buffer_->transform(stamped_pose, transformed_pose, "base_link");

            // Check if goal is reachable
            double distance = calculateDistance(transformed_pose.pose, getCurrentPose().pose);
            if (distance > max_navigation_distance_) {
                RCLCPP_WARN(this->get_logger(), "Goal too far: %f > %f", distance, max_navigation_distance_);
                return false;
            }

            return true;
        } catch (const tf2::TransformException& ex) {
            RCLCPP_ERROR(this->get_logger(), "Transform failed: %s", ex.what());
            return false;
        }
    }

    bool getCurrentPose(geometry_msgs::msg::PoseStamped& pose) const {
        try {
            geometry_msgs::msg::TransformStamped transform = tf_buffer_->lookupTransform(
                "map", "base_link", tf2::TimePointZero);

            pose.header.frame_id = "map";
            pose.header.stamp = transform.header.stamp;
            pose.pose.position.x = transform.transform.translation.x;
            pose.pose.position.y = transform.transform.translation.y;
            pose.pose.position.z = transform.transform.translation.z;
            pose.pose.orientation = transform.transform.rotation;

            return true;
        } catch (const tf2::TransformException& ex) {
            RCLCPP_ERROR(this->get_logger(), "Could not get current pose: %s", ex.what());
            return false;
        }
    }

    double calculateDistance(const geometry_msgs::msg::Pose& p1,
                           const geometry_msgs::msg::Pose& p2) const {
        double dx = p1.position.x - p2.position.x;
        double dy = p1.position.y - p2.position.y;
        double dz = p1.position.z - p2.position.z;
        return std::sqrt(dx*dx + dy*dy + dz*dz);
    }

    // Parameters
    double goal_tolerance_ = 0.3;  // meters
    double max_navigation_distance_ = 50.0;  // meters
    geometry_msgs::msg::Pose current_start_pose_;
};

// Action client for sending navigation goals
class NavigationActionClient : public rclcpp::Node
{
public:
    explicit NavigationActionClient(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
    : Node("navigation_action_client", options)
    {
        this->client_ptr_ = rclcpp_action::create_client<NavigateToPose>(
            this->get_node_base_interface(),
            this->get_node_graph_interface(),
            this->get_node_logging_interface(),
            this->get_node_waitables_interface(),
            "navigate_to_pose");

        this->timer_ = this->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&NavigationActionClient::sendGoal, this));
    }

private:
    rclcpp_action::Client<NavigateToPose>::SharedPtr client_ptr_;
    rclcpp::TimerBase::SharedPtr timer_;
    bool goal_sent_ = false;

    void sendGoal()
    {
        using namespace std::placeholders;

        if (!client_ptr_->wait_for_action_server(std::chrono::seconds(5))) {
            RCLCPP_ERROR(this->get_logger(), "Action server not available after waiting");
            return;
        }

        auto goal_msg = NavigateToPose::Goal();
        goal_msg.pose.header.frame_id = "map";
        goal_msg.pose.header.stamp = this->get_clock()->now();
        goal_msg.pose.pose.position.x = 1.0;
        goal_msg.pose.pose.position.y = 1.0;
        goal_msg.pose.pose.orientation.w = 1.0;

        auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
        send_goal_options.result_callback = std::bind(&NavigationActionClient::resultCallback, this, _1);
        send_goal_options.feedback_callback = std::bind(&NavigationActionClient::feedbackCallback, this, _1, _2);

        RCLCPP_INFO(this->get_logger(), "Sending navigation goal");
        client_ptr_->async_send_goal(goal_msg, send_goal_options);
        goal_sent_ = true;

        // Stop the timer after sending one goal
        timer_->cancel();
    }

    void resultCallback(const rclcpp_action::ClientGoalHandle<NavigateToPose>::WrappedResult & result)
    {
        switch (result.code) {
            case rclcpp_action::ResultCode::SUCCEEDED:
                RCLCPP_INFO(this->get_logger(), "Navigation succeeded!");
                break;
            case rclcpp_action::ResultCode::ABORTED:
                RCLCPP_ERROR(this->get_logger(), "Navigation was aborted");
                return;
            case rclcpp_action::ResultCode::CANCELED:
                RCLCPP_INFO(this->get_logger(), "Navigation was canceled");
                return;
            default:
                RCLCPP_ERROR(this->get_logger(), "Unknown result code");
                return;
        }

        rclcpp::shutdown();
    }

    void feedbackCallback(
        rclcpp_action::ClientGoalHandle<NavigateToPose>::SharedPtr,
        const std::shared_ptr<const NavigateToPose::Feedback> feedback)
    {
        RCLCPP_INFO(this->get_logger(),
                   "Distance to goal: %.2f, Distance traveled: %.2f",
                   feedback->distance_remaining, feedback->distance_traveled);
    }
};
```

## Behavior Trees for Navigation

### Complex Navigation Decision Making

```cpp
// behavior_tree_navigator.cpp
#include <behaviortree_cpp_v3/bt_factory.h>
#include <behaviortree_cpp_v3/loggers/bt_cout_logger.h>
#include <nav2_behavior_tree/bt_action_node.hpp>
#include <nav2_behavior_tree/bt_conversions.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <nav2_msgs/action/navigate_to_pose.hpp>

// Custom behavior tree nodes for humanoid navigation
class HumanoidNavigateToPoseAction_BT : public BT::RosActionNode<NavigateToPose>
{
public:
    HumanoidNavigateToPoseAction_BT(
        const std::string & xml_tag_name,
        const BT::NodeConfiguration & conf)
    : RosActionNode<NavigateToPose>(xml_tag_name, conf)
    {}

    static BT::PortsList providedPorts()
    {
        return providedBasicPorts({
            BT::InputPort<geometry_msgs::msg::PoseStamped>("goal", "Destination to navigate to"),
            BT::InputPort<std::string>("behavior_tree", "XML defining the behavior tree to execute on arrival")
        });
    }

private:
    geometry_msgs::msg::PoseStamped goal_;

    bool setGoal(RosActionNode::Goal & goal) override
    {
        getInput("goal", goal.pose);
        return true;
    }

    void onResultReceived(const WrappedResult & wr) override
    {
        if (wr.result->error_code == NavigateToPose::Result::SUCCESS) {
            setStatus(BT::NodeStatus::SUCCESS);
        } else {
            setStatus(BT::NodeStatus::FAILURE);
        }
    }

    void onHalted() override
    {
        RCLCPP_INFO(node_->get_logger(), "Navigation action was halted");
    }
};

// Behavior tree for complex navigation tasks
class ComplexNavigationBT : public rclpp::Node
{
public:
    ComplexNavigationBT(const std::string& name, const std::string& ns = "")
        : Node(name, ns)
    {
        // Create behavior tree factory
        factory_ = std::make_shared<BT::BehaviorTreeFactory>();

        // Register custom nodes
        factory_->registerNodeType<HumanoidNavigateToPoseAction_BT>("HumanoidNavigateToPose");
        factory_->registerNodeType<CheckHumanPresenceCondition>("CheckHumanPresence");
        factory_->registerNodeType<WaitForPassageAction>("WaitForPassage");
        factory_->registerNodeType<ApproachObjectAction>("ApproachObject");
        factory_->registerNodeType<AvoidDynamicObstacleAction>("AvoidDynamicObstacle");
        factory_->registerNodeType<ReplanPathAction>("ReplanPath");

        // Create the behavior tree
        createBehaviorTree();
    }

private:
    std::shared_ptr<BT::BehaviorTreeFactory> factory_;
    std::unique_ptr<BT::Tree> tree_;
    std::unique_ptr<BT::Blackboard::Ptr> blackboard_;

    void createBehaviorTree()
    {
        // Complex navigation behavior tree XML
        std::string xml_string = R"(
        <root main_tree_to_execute="MainTree">
            <BehaviorTree ID="MainTree">
                <Sequence>
                    <CheckHumanPresenceCondition />
                    <Fallback>
                        <Sequence>
                            <WaitForPassageAction timeout="10.0" />
                            <HumanoidNavigateToPose goal="{goal_pose}" />
                        </Sequence>
                        <Sequence>
                            <ReplanPathAction alternative_goals="{alternative_goals}" />
                            <HumanoidNavigateToPose goal="{alternative_goal}" />
                        </Sequence>
                    </Fallback>
                    <ApproachObjectAction object_type="target_object" />
                </Sequence>
            </BehaviorTree>
        </root>
        )";

        // Create blackboard
        blackboard_ = BT::Blackboard::create();

        // Build tree
        tree_ = std::make_unique<BT::Tree>(factory_->createTreeFromText(xml_string, blackboard_));

        // Create logger
        logger_ = std::make_unique<BT::StdCoutLogger>(*tree_);
    }

    // Condition node: Check for human presence
    class CheckHumanPresenceCondition : public BT::ConditionNode
    {
    public:
        CheckHumanPresenceCondition(const std::string& name, const BT::NodeConfiguration& config)
            : BT::ConditionNode(name, config) {}

        static BT::PortsList providedPorts() {
            return { BT::InputPort<double>("detection_range", 2.0, "Range to detect humans") };
        }

        BT::NodeStatus tick() override {
            double range;
            if (!getInput("detection_range", range)) {
                throw BT::RuntimeError("Missing required input: detection_range");
            }

            // Check for humans in the path
            bool human_detected = checkForHumansInRange(range);

            return human_detected ? BT::NodeStatus::FAILURE : BT::NodeStatus::SUCCESS;
        }

    private:
        bool checkForHumansInRange(double range) {
            // Implementation to check for humans using perception system
            // This would interface with the vision system
            return false; // Simplified for example
        }
    };

    // Action node: Wait for passage
    class WaitForPassageAction : public BT::ActionNodeBase
    {
    public:
        WaitForPassageAction(const std::string& name, const BT::NodeConfiguration& config)
            : BT::ActionNodeBase(name, config) {}

        static BT::PortsList providedPorts() {
            return { BT::InputPort<double>("timeout", 10.0, "Timeout for waiting") };
        }

        BT::NodeStatus tick() override {
            if (status() == BT::NodeStatus::IDLE) {
                // Start waiting
                start_time_ = std::chrono::steady_clock::now();

                // Get timeout
                double timeout;
                if (!getInput("timeout", timeout)) {
                    timeout = 10.0;
                }
                timeout_ = std::chrono::duration<double>(timeout);

                return BT::NodeStatus::RUNNING;
            }

            // Check if timeout occurred
            auto now = std::chrono::steady_clock::now();
            if (now - start_time_ > timeout_) {
                return BT::NodeStatus::FAILURE;
            }

            // Check if path is clear
            if (isPathClear()) {
                return BT::NodeStatus::SUCCESS;
            }

            return BT::NodeStatus::RUNNING;
        }

        void halt() override {
            setStatus(BT::NodeStatus::IDLE);
        }

    private:
        std::chrono::steady_clock::time_point start_time_;
        std::chrono::duration<double> timeout_;

        bool isPathClear() {
            // Check if path is now clear of obstacles/humans
            return true; // Simplified for example
        }
    };

    // Action node: Approach object
    class ApproachObjectAction : public BT::ActionNodeBase
    {
    public:
        ApproachObjectAction(const std::string& name, const BT::NodeConfiguration& config)
            : BT::ActionNodeBase(name, config) {}

        static BT::PortsList providedPorts() {
            return { BT::InputPort<std::string>("object_type", "Object type to approach") };
        }

        BT::NodeStatus tick() override {
            if (status() == BT::NodeStatus::IDLE) {
                // Get object type
                std::string object_type;
                if (!getInput("object_type", object_type)) {
                    throw BT::RuntimeError("Missing required input: object_type");
                }

                // Find object and approach
                bool success = approachObject(object_type);
                return success ? BT::NodeStatus::SUCCESS : BT::NodeStatus::FAILURE;
            }

            return BT::NodeStatus::RUNNING;
        }

        void halt() override {
            setStatus(BT::NodeStatus::IDLE);
        }

    private:
        bool approachObject(const std::string& object_type) {
            // Implementation to approach a specific object type
            // This would use perception to locate the object and navigate to it
            return true; // Simplified for example
        }
    };
};

// Recovery behaviors for navigation failures
class RecoveryNode : public BT::ActionNodeBase
{
public:
    RecoveryNode(const std::string& name, const BT::NodeConfiguration& config)
        : BT::ActionNodeBase(name, config) {}

    static BT::PortsList providedPorts() {
        return {
            BT::InputPort<std::string>("recovery_behavior", "Type of recovery to execute"),
            BT::InputPort<double>("timeout", 5.0, "Recovery timeout")
        };
    }

    BT::NodeStatus tick() override {
        if (status() == BT::NodeStatus::IDLE) {
            std::string behavior;
            double timeout;

            if (!getInput("recovery_behavior", behavior)) {
                throw BT::RuntimeError("Missing required input: recovery_behavior");
            }
            if (!getInput("timeout", timeout)) {
                timeout = 5.0;
            }

            start_time_ = std::chrono::steady_clock::now();
            timeout_ = std::chrono::duration<double>(timeout);

            if (behavior == "spin") {
                return executeSpinRecovery();
            } else if (behavior == "backup") {
                return executeBackupRecovery();
            } else if (behavior == "wait") {
                return executeWaitRecovery();
            } else {
                RCLCPP_ERROR(node_->get_logger(), "Unknown recovery behavior: %s", behavior.c_str());
                return BT::NodeStatus::FAILURE;
            }
        }

        // Check for timeout
        auto now = std::chrono::steady_clock::now();
        if (now - start_time_ > timeout_) {
            RCLCPP_WARN(node_->get_logger(), "Recovery behavior timed out");
            return BT::NodeStatus::FAILURE;
        }

        return BT::NodeStatus::RUNNING;
    }

    void halt() override {
        setStatus(BT::NodeStatus::IDLE);
    }

private:
    std::chrono::steady_clock::time_point start_time_;
    std::chrono::duration<double> timeout_;

    BT::NodeStatus executeSpinRecovery() {
        // Execute spinning recovery behavior
        // For humanoid, this might involve turning in place to reassess
        return BT::NodeStatus::SUCCESS;
    }

    BT::NodeStatus executeBackupRecovery() {
        // Execute backing up recovery behavior
        // For humanoid, this might involve stepping back
        return BT::NodeStatus::SUCCESS;
    }

    BT::NodeStatus executeWaitRecovery() {
        // Execute waiting recovery behavior
        // Wait for dynamic obstacles to clear
        return BT::NodeStatus::SUCCESS;
    }
};
```

## Humanoid-Specific Navigation Behaviors

### Balance-Aware Navigation

```cpp
// humanoid_navigation_behaviors.cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <cmath>

class HumanoidNavigationController : public rclpp::Node
{
public:
    HumanoidNavigationController()
        : Node("humanoid_navigation_controller")
    {
        // Publishers and subscribers
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&HumanoidNavigationController::imuCallback, this, std::placeholders::_1));
        odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "odom", 10, std::bind(&HumanoidNavigationController::odomCallback, this, std::placeholders::_1));

        // Parameters for humanoid-specific navigation
        this->declare_parameter("max_linear_velocity", 0.4);      // m/s
        this->declare_parameter("max_angular_velocity", 0.6);     // rad/s
        this->declare_parameter("balance_threshold", 0.1);        // tilt threshold in radians
        this->declare_parameter("step_size", 0.1);               // step size in meters
        this->declare_parameter("step_height", 0.05);            // step height in meters
        this->declare_parameter("stance_width", 0.2);            // stance width in meters
        this->declare_parameter("zmp_margin", 0.05);             // Zero Moment Point safety margin

        // Get parameters
        max_linear_vel_ = this->get_parameter("max_linear_velocity").as_double();
        max_angular_vel_ = this->get_parameter("max_angular_velocity").as_double();
        balance_threshold_ = this->get_parameter("balance_threshold").as_double();
        step_size_ = this->get_parameter("step_size").as_double();
        step_height_ = this->get_parameter("step_height").as_double();
        stance_width_ = this->get_parameter("stance_width").as_double();
        zmp_margin_ = this->get_parameter("zmp_margin").as_double();

        // Initialize state
        current_balance_state_ = BalanceState::STABLE;
        is_stepping_ = false;

        RCLCPP_INFO(this->get_logger(), "Humanoid Navigation Controller initialized");
    }

private:
    // Publishers/subscribers
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

    // Parameters
    double max_linear_vel_;
    double max_angular_vel_;
    double balance_threshold_;
    double step_size_;
    double step_height_;
    double stance_width_;
    double zmp_margin_;

    // State variables
    sensor_msgs::msg::Imu current_imu_;
    nav_msgs::msg::Odometry current_odom_;
    enum class BalanceState { STABLE, UNSTABLE, RECOVERING };
    BalanceState current_balance_state_;
    bool is_stepping_;
    rclcpp::Time last_step_time_;

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        current_imu_ = *msg;

        // Check balance state based on IMU data
        double roll, pitch, yaw;
        tf2::Quaternion quat(
            msg->orientation.x,
            msg->orientation.y,
            msg->orientation.z,
            msg->orientation.w
        );
        tf2::Matrix3x3(quat).getRPY(roll, pitch, yaw);

        // Check if tilt exceeds threshold
        if (std::abs(roll) > balance_threshold_ || std::abs(pitch) > balance_threshold_) {
            if (current_balance_state_ == BalanceState::STABLE) {
                RCLCPP_WARN(this->get_logger(), "Balance instability detected: roll=%.3f, pitch=%.3f", roll, pitch);
            }
            current_balance_state_ = BalanceState::UNSTABLE;
        } else {
            if (current_balance_state_ == BalanceState::UNSTABLE) {
                RCLCPP_INFO(this->get_logger(), "Balance recovered");
            }
            current_balance_state_ = BalanceState::STABLE;
        }
    }

    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        current_odom_ = *msg;
    }

    geometry_msgs::msg::Twist generateHumanoidVelocityCommand(
        const geometry_msgs::msg::Pose& target_pose,
        const geometry_msgs::msg::Pose& current_pose) {

        geometry_msgs::msg::Twist cmd_vel;

        // Calculate distance and angle to target
        double dx = target_pose.position.x - current_pose.position.x;
        double dy = target_pose.position.y - current_pose.position.y;
        double distance_to_target = std::sqrt(dx*dx + dy*dy);

        // Calculate target angle
        double target_angle = std::atan2(dy, dx);
        double current_yaw = getYawFromPose(current_pose);
        double angle_diff = target_angle - current_yaw;

        // Normalize angle difference
        while (angle_diff > M_PI) angle_diff -= 2 * M_PI;
        while (angle_diff < -M_PI) angle_diff += 2 * M_PI;

        // Humanoid-specific velocity generation with balance considerations
        if (current_balance_state_ == BalanceState::UNSTABLE) {
            // Emergency stop if balance is compromised
            cmd_vel.linear.x = 0.0;
            cmd_vel.angular.z = 0.0;
            RCLCPP_WARN(this->get_logger(), "Balance compromised - stopping navigation");
        } else {
            // Calculate velocities based on distance and angle
            double linear_vel = 0.0;
            double angular_vel = 0.0;

            // Linear velocity based on distance (proportional with saturation)
            linear_vel = std::min(max_linear_vel_ * 0.8,  // Conservative speed for balance
                                 std::max(0.05, distance_to_target * 0.5));  // Minimum 5 cm/s

            // Angular velocity based on angle difference (with smoothing)
            angular_vel = std::min(max_angular_vel_ * 0.7,  // Conservative for balance
                                  std::max(-max_angular_vel_ * 0.7, angle_diff * 1.0));

            // Apply humanoid-specific constraints
            cmd_vel.linear.x = applyHumanoidConstraints(linear_vel, NavigationAxis::FORWARD);
            cmd_vel.angular.z = applyHumanoidConstraints(angular_vel, NavigationAxis::ROTATION);

            // Ensure smooth acceleration/deceleration
            cmd_vel.linear.x = limitAcceleration(cmd_vel.linear.x, last_linear_vel_);
            cmd_vel.angular.z = limitAcceleration(cmd_vel.angular.z, last_angular_vel_);

            last_linear_vel_ = cmd_vel.linear.x;
            last_angular_vel_ = cmd_vel.angular.z;
        }

        return cmd_vel;
    }

    double applyHumanoidConstraints(double velocity, NavigationAxis axis) {
        // Apply humanoid-specific constraints based on navigation axis
        switch (axis) {
            case NavigationAxis::FORWARD:
                // Forward movement constraints for stable walking
                return std::max(-max_linear_vel_ * 0.5,  // Limited backward speed
                               std::min(max_linear_vel_, velocity));
            case NavigationAxis::LATERAL:
                // Lateral movement (sidestepping) - more conservative
                return std::max(-max_linear_vel_ * 0.3,  // Very limited lateral movement
                               std::min(max_linear_vel_ * 0.3, velocity));
            case NavigationAxis::ROTATION:
                // Rotation constraints for stable turning
                return std::max(-max_angular_vel_, std::min(max_angular_vel_, velocity));
            default:
                return velocity;
        }
    }

    double limitAcceleration(double target_vel, double current_vel) {
        // Limit acceleration to prevent balance loss
        const double max_linear_acc = 0.3;  // m/s²
        const double max_angular_acc = 0.5; // rad/s²

        double dt = 0.1;  // Assume 10Hz control loop
        double max_delta_vel = (axis == NavigationAxis::ROTATION) ? max_angular_acc * dt : max_linear_acc * dt;

        double delta_vel = target_vel - current_vel;
        delta_vel = std::max(-max_delta_vel, std::min(max_delta_vel, delta_vel));

        return current_vel + delta_vel;
    }

    double getYawFromPose(const geometry_msgs::msg::Pose& pose) {
        tf2::Quaternion quat(pose.orientation.x, pose.orientation.y,
                            pose.orientation.z, pose.orientation.w);
        double roll, pitch, yaw;
        tf2::Matrix3x3(quat).getRPY(roll, pitch, yaw);
        return yaw;
    }

    enum class NavigationAxis { FORWARD, LATERAL, ROTATION };

    double last_linear_vel_ = 0.0;
    double last_angular_vel_ = 0.0;
};

// Humanoid path follower with balance awareness
class HumanoidPathFollower
{
public:
    HumanoidPathFollower()
    {
        // Initialize with humanoid-specific parameters
        lookahead_distance_ = 0.5;  // 50cm lookahead
        path_following_gain_ = 1.0;
        balance_safety_factor_ = 0.8;  // Conservative for balance
    }

    NavigationResult followPath(const PathPlan& path, const Pose& current_pose)
    {
        NavigationResult result;
        result.status = NavigationStatus::IN_PROGRESS;

        if (path.isEmpty()) {
            result.status = NavigationStatus::FAILURE;
            result.message = "Empty path";
            return result;
        }

        // Get current path segment
        PathSegment current_segment = path.getCurrentSegment(current_pose);

        if (current_segment.isEmpty()) {
            result.status = NavigationStatus::FAILURE;
            result.message = "Could not find current segment on path";
            return result;
        }

        // Calculate velocity command
        geometry_msgs::msg::Twist cmd_vel = calculatePathFollowingCommand(
            current_pose, current_segment, path);

        // Check balance before executing command
        if (isBalanceCompromised()) {
            cmd_vel.linear.x = 0.0;
            cmd_vel.angular.z = 0.0;
            result.status = NavigationStatus::STUCK;
            result.message = "Balance compromised during path following";
        } else {
            // Publish command
            publishVelocityCommand(cmd_vel);

            // Check if we've reached the end of the current segment
            if (isAtSegmentEnd(current_pose, current_segment)) {
                result.status = NavigationStatus::PROGRESS;
            }

            // Check if we're close to the final goal
            if (isNearGoal(current_pose, path.getGoal())) {
                result.status = NavigationStatus::SUCCESS;
            }
        }

        return result;
    }

private:
    double lookahead_distance_;
    double path_following_gain_;
    double balance_safety_factor_;

    geometry_msgs::msg::Twist calculatePathFollowingCommand(
        const Pose& current_pose,
        const PathSegment& segment,
        const PathPlan& path) {

        geometry_msgs::msg::Twist cmd_vel;

        // Calculate cross-track error (distance from path)
        double crosstrack_error = calculateCrosstrackError(current_pose, segment);

        // Calculate along-track distance to goal
        double alongtrack_distance = calculateAlongtrackDistance(current_pose, segment);

        // Pure pursuit algorithm with lookahead
        Pose lookahead_point = calculateLookaheadPoint(current_pose, segment, lookahead_distance_);

        // Calculate heading to lookahead point
        double target_angle = std::atan2(
            lookahead_point.position.y - current_pose.position.y,
            lookahead_point.position.x - current_pose.position.x
        );

        double current_yaw = getCurrentYaw();
        double heading_error = target_angle - current_yaw;

        // Normalize heading error
        while (heading_error > M_PI) heading_error -= 2 * M_PI;
        while (heading_error < -M_PI) heading_error += 2 * M_PI;

        // Calculate velocities
        double linear_vel = std::min(max_linear_vel_,
                                    std::max(0.05, alongtrack_distance * path_following_gain_));

        // Apply balance-aware angular control
        double angular_vel = heading_error * path_following_gain_ * balance_safety_factor_;

        // Apply humanoid constraints
        cmd_vel.linear.x = applyHumanoidConstraints(linear_vel, NavigationAxis::FORWARD);
        cmd_vel.angular.z = applyHumanoidConstraints(angular_vel, NavigationAxis::ROTATION);

        // If cross-track error is too large, consider path blocked
        if (std::abs(crosstrack_error) > 0.5) {  // 50cm tolerance
            cmd_vel.linear.x = 0.0;  // Stop forward motion
            result.status = NavigationStatus::BLOCKED;
            result.message = "Too far from path - possible obstacle";
        }

        return cmd_vel;
    }

    Pose calculateLookaheadPoint(const Pose& current_pose,
                               const PathSegment& segment,
                               double lookahead_distance) {
        // Calculate point along path at lookahead distance
        // This is a simplified implementation - in practice, this would use
        // more sophisticated path interpolation

        double current_yaw = getCurrentYaw();
        double lookahead_x = current_pose.position.x + lookahead_distance * cos(current_yaw);
        double lookahead_y = current_pose.position.y + lookahead_distance * sin(current_yaw);

        Pose lookahead_point;
        lookahead_point.position.x = lookahead_x;
        lookahead_point.position.y = lookahead_y;
        lookahead_point.position.z = current_pose.position.z;  // Maintain height

        return lookahead_point;
    }

    double calculateCrosstrackError(const Pose& current_pose, const PathSegment& segment) {
        // Calculate perpendicular distance from current position to path segment
        // Simplified implementation - assumes straight line segment
        double segment_dx = segment.getEnd().position.x - segment.getStart().position.x;
        double segment_dy = segment.getEnd().position.y - segment.getStart().position.y;
        double segment_length = std::sqrt(segment_dx*segment_dx + segment_dy*segment_dy);

        if (segment_length < 0.01) return 0.0;  // Degenerate segment

        // Normalize segment direction
        double norm_dx = segment_dx / segment_length;
        double norm_dy = segment_dy / segment_length;

        // Vector from segment start to current position
        double to_current_x = current_pose.position.x - segment.getStart().position.x;
        double to_current_y = current_pose.position.y - segment.getStart().position.y;

        // Project onto segment
        double projection = to_current_x * norm_dx + to_current_y * norm_dy;
        projection = std::max(0.0, std::min(segment_length, projection));  // Clamp to segment

        // Calculate closest point on segment
        double closest_x = segment.getStart().position.x + projection * norm_dx;
        double closest_y = segment.getStart().position.y + projection * norm_dy;

        // Calculate cross-track error
        double error_x = current_pose.position.x - closest_x;
        double error_y = current_pose.position.y - closest_y;
        double crosstrack_error = std::sqrt(error_x*error_x + error_y*error_y);

        return crosstrack_error;
    }

    bool isBalanceCompromised() const {
        // Check if current balance state indicates instability
        // This would interface with the balance controller
        return false; // Simplified for example
    }

    bool isAtSegmentEnd(const Pose& current_pose, const PathSegment& segment) const {
        double distance_to_end = std::sqrt(
            std::pow(current_pose.position.x - segment.getEnd().position.x, 2) +
            std::pow(current_pose.position.y - segment.getEnd().position.y, 2)
        );
        return distance_to_end < 0.2;  // 20cm tolerance
    }

    bool isNearGoal(const Pose& current_pose, const Pose& goal) const {
        double distance = std::sqrt(
            std::pow(current_pose.position.x - goal.position.x, 2) +
            std::pow(current_pose.position.y - goal.position.y, 2)
        );
        return distance < 0.3;  // 30cm goal tolerance for humanoid feet placement
    }

    double getCurrentYaw() const {
        // Get current yaw from odometry or IMU
        return 0.0; // Simplified for example
    }

    void publishVelocityCommand(const geometry_msgs::msg::Twist& cmd_vel) {
        // Publish command to robot's base controller
        // This would be implemented based on the specific humanoid platform
    }
};
```

## Integration with Vision-Language Systems

### Semantic Navigation Behaviors

```cpp
// semantic_navigation.cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <std_msgs/msg/string.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>
#include <object_recognition_msgs/msg/recognized_object_array.hpp>

class SemanticNavigationManager : public rclcpp::Node
{
public:
    SemanticNavigationManager()
        : Node("semantic_navigation_manager")
    {
        // Subscriptions
        command_sub_ = this->create_subscription<std_msgs::msg::String>(
            "vla_commands", 10,
            std::bind(&SemanticNavigationManager::commandCallback, this, std::placeholders::_1));

        object_detections_sub_ = this->create_subscription<vision_msgs::msg::Detection2DArray>(
            "object_detections", 10,
            std::bind(&SemanticNavigationManager::detectionCallback, this, std::placeholders::_1));

        // Publishers
        navigation_goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
            "navigation_goal", 10);

        feedback_pub_ = this->create_publisher<std_msgs::msg::String>(
            "navigation_feedback", 10);

        RCLCPP_INFO(this->get_logger(), "Semantic Navigation Manager initialized");
    }

private:
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr command_sub_;
    rclcpp::Subscription<vision_msgs::msg::Detection2DArray>::SharedPtr object_detections_sub_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr navigation_goal_pub_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr feedback_pub_;

    std::map<std::string, geometry_msgs::msg::Pose> known_object_locations_;

    void commandCallback(const std_msgs::msg::String::SharedPtr msg)
    {
        std::string command = msg->data;
        RCLCPP_INFO(this->get_logger(), "Received navigation command: %s", command.c_str());

        // Parse the command to extract semantic information
        SemanticNavigationRequest request = parseNavigationCommand(command);

        if (request.isValid()) {
            // Resolve semantic goal to physical coordinates
            geometry_msgs::msg::PoseStamped goal_pose = resolveSemanticGoal(request);

            if (goal_pose.header.frame_id != "") {
                // Publish navigation goal
                navigation_goal_pub_->publish(goal_pose);

                // Provide feedback
                std_msgs::msg::String feedback_msg;
                feedback_msg.data = "Navigating to " + request.target_object + " in the " + request.target_location;
                feedback_pub_->publish(feedback_msg);
            } else {
                // Goal resolution failed
                std_msgs::msg::String feedback_msg;
                feedback_msg.data = "Could not locate " + request.target_object;
                feedback_pub_->publish(feedback_msg);
            }
        } else {
            std_msgs::msg::String feedback_msg;
            feedback_msg.data = "Could not understand navigation command: " + command;
            feedback_pub_->publish(feedback_msg);
        }
    }

    void detectionCallback(const vision_msgs::msg::Detection2DArray::SharedPtr msg)
    {
        // Update known object locations based on detections
        for (const auto& detection : msg->detections) {
            if (!detection.results.empty()) {
                std::string object_name = detection.results[0].hypothesis.name;

                // In a real system, you'd get the 3D position from the detection
                // For now, we'll just store the fact that the object was seen
                if (known_object_locations_.find(object_name) == known_object_locations_.end()) {
                    // This is a new object - could potentially update map
                    RCLCPP_INFO(this->get_logger(), "Discovered new object: %s", object_name.c_str());
                }
            }
        }
    }

    struct SemanticNavigationRequest {
        std::string command_text;
        std::string target_object;
        std::string target_location;
        std::string action_type;  // "navigate_to", "find_and_go", "avoid", etc.
        bool isValid() const { return !target_object.empty(); }
    };

    SemanticNavigationRequest parseNavigationCommand(const std::string& command) const
    {
        SemanticNavigationRequest request;
        request.command_text = command;

        std::string lower_command = command;
        std::transform(lower_command.begin(), lower_command.end(), lower_command.begin(), ::tolower);

        // Simple keyword-based parsing (in practice, use NLP)
        if (lower_command.find("go to") != std::string::npos) {
            request.action_type = "navigate_to";
            // Extract target from command
            size_t pos = lower_command.find("go to");
            std::string target_part = lower_command.substr(pos + 5);  // After "go to"
            request.target_object = extractObjectName(target_part);
        } else if (lower_command.find("find") != std::string::npos) {
            request.action_type = "find_and_go";
            // Extract target object
            size_t pos = lower_command.find("find");
            std::string target_part = lower_command.substr(pos + 4);  // After "find"
            request.target_object = extractObjectName(target_part);
        } else if (lower_command.find("avoid") != std::string::npos) {
            request.action_type = "avoid";
            // Extract object to avoid
            size_t pos = lower_command.find("avoid");
            std::string target_part = lower_command.substr(pos + 5);  // After "avoid"
            request.target_object = extractObjectName(target_part);
        }

        // Extract location if specified
        if (lower_command.find("in the") != std::string::npos) {
            size_t pos = lower_command.find("in the");
            std::string location_part = lower_command.substr(pos + 6);  // After "in the"
            request.target_location = extractLocationName(location_part);
        }

        return request;
    }

    std::string extractObjectName(const std::string& text) const
    {
        // Simple object name extraction (in practice, use proper NLP)
        std::vector<std::string> object_names = {
            "cup", "book", "ball", "box", "chair", "table", "kitchen", "bedroom", "office", "couch"
        };

        for (const auto& obj_name : object_names) {
            if (text.find(obj_name) != std::string::npos) {
                return obj_name;
            }
        }

        return "";  // No object found
    }

    std::string extractLocationName(const std::string& text) const
    {
        // Simple location name extraction
        std::vector<std::string> location_names = {
            "kitchen", "bedroom", "living room", "office", "bathroom", "hallway"
        };

        for (const auto& loc_name : location_names) {
            if (text.find(loc_name) != std::string::npos) {
                return loc_name;
            }
        }

        return "";  // No location found
    }

    geometry_msgs::msg::PoseStamped resolveSemanticGoal(const SemanticNavigationRequest& request)
    {
        geometry_msgs::msg::PoseStamped goal_pose;

        // First, check if we know the location of the target object
        auto it = known_object_locations_.find(request.target_object);
        if (it != known_object_locations_.end()) {
            // Use known location
            goal_pose.pose = it->second;
            goal_pose.header.frame_id = "map";
            goal_pose.header.stamp = this->get_clock()->now();
            return goal_pose;
        }

        // If not known, check if it's a location name
        if (request.target_location != "") {
            // In a real system, this would look up location coordinates
            // For now, we'll return an invalid pose
            return geometry_msgs::msg::PoseStamped{};  // Invalid
        }

        // If it's an object we don't know, we need to search for it
        // This would trigger a search behavior in the navigation system
        RCLCPP_INFO(this->get_logger(), "Need to search for object: %s", request.target_object.c_str());

        // For now, return invalid pose indicating search is needed
        return geometry_msgs::msg::PoseStamped{};
    }
};

// Integration with VLA systems
class VLANavigationIntegrator
{
public:
    VLANavigationIntegrator()
    {
        // Initialize the connection between VLA system and navigation system
    }

    NavigationResult ExecuteVLANavigationCommand(const std::string& command,
                                              const SceneGraph& current_scene,
                                              const Pose& current_pose)
    {
        // Parse VLA command
        auto parsed_command = ParseVLANavigationCommand(command);

        if (!parsed_command.IsValid()) {
            return NavigationResult{NavigationStatus::INVALID_COMMAND, "Could not parse navigation command"};
        }

        // Resolve semantic goal
        auto semantic_resolver = std::make_shared<SemanticGoalResolver>();
        auto resolution_result = semantic_resolver->ResolveGoal(parsed_command, current_scene);

        if (!resolution_result.success) {
            return NavigationResult{NavigationStatus::INVALID_GOAL, resolution_result.error_message};
        }

        // Generate navigation plan with semantic constraints
        auto planner = std::make_unique<SemanticPathPlanner>();
        auto path_plan = planner->PlanPathWithSemantics(
            current_pose,
            resolution_result.resolved_pose,
            parsed_command.semantic_constraints,
            current_scene
        );

        if (path_plan.IsEmpty()) {
            return NavigationResult{NavigationStatus::NO_PATH_FOUND, "Could not find path with semantic constraints"};
        }

        // Execute navigation with continuous semantic monitoring
        auto executor = std::make_unique<SemanticNavigationExecutor>();
        auto execution_result = executor->ExecutePathWithMonitoring(
            path_plan,
            parsed_command,
            current_scene
        );

        // Provide semantic feedback
        ProvideSemanticNavigationFeedback(execution_result, command);

        return execution_result;
    }

private:
    struct ParsedVLANavigationCommand {
        std::string original_command;
        std::string action_type;      // "navigate", "find_object", "go_to_location", etc.
        std::string target_object;    // Object to navigate to/find
        std::string target_location;  // Location to navigate to
        std::vector<SemanticConstraint> semantic_constraints;  // Constraints from command
        bool IsValid() const { return !action_type.empty(); }
    };

    ParsedVLANavigationCommand ParseVLANavigationCommand(const std::string& command)
    {
        ParsedVLANavigationCommand parsed;

        // This would use a proper NLP parser in a real system
        // For now, using simple keyword matching
        std::string lower_command = command;
        std::transform(lower_command.begin(), lower_command.end(), lower_command.begin(), ::tolower);

        parsed.original_command = command;

        // Extract action type
        if (lower_command.find("go to") != std::string::npos) {
            parsed.action_type = "navigate";
        } else if (lower_command.find("find") != std::string::npos) {
            parsed.action_type = "find_object";
        } else if (lower_command.find("bring") != std::string::npos) {
            parsed.action_type = "fetch_object";
        }

        // Extract target object
        std::vector<std::string> common_objects = {
            "cup", "book", "ball", "box", "bottle", "chair", "table", "person"
        };

        for (const auto& obj : common_objects) {
            if (lower_command.find(obj) != std::string::npos) {
                parsed.target_object = obj;
                break;
            }
        }

        // Extract target location
        std::vector<std::string> common_locations = {
            "kitchen", "bedroom", "living room", "office", "dining room"
        };

        for (const auto& loc : common_locations) {
            if (lower_command.find(loc) != std::string::npos) {
                parsed.target_location = loc;
                break;
            }
        }

        // Extract semantic constraints
        if (lower_command.find("carefully") != std::string::npos ||
            lower_command.find("slowly") != std::string::npos) {
            SemanticConstraint safety_constraint;
            safety_constraint.constraint_type = "speed_limit";
            safety_constraint.value = 0.2;  // Slow speed
            safety_constraint.importance = 2.0;  // High importance
            parsed.semantic_constraints.push_back(safety_constraint);
        }

        if (lower_command.find("around") != std::string::npos) {
            SemanticConstraint avoid_constraint;
            avoid_constraint.constraint_type = "avoid_object";
            avoid_constraint.object_type = parsed.target_object;  // Interpret "go around object"
            avoid_constraint.importance = 1.5;
            parsed.semantic_constraints.push_back(avoid_constraint);
        }

        return parsed;
    }

    void ProvideSemanticNavigationFeedback(const NavigationResult& result, const std::string& original_command)
    {
        std::string feedback;

        if (result.status == NavigationStatus::SUCCESS) {
            feedback = "Successfully navigated to the requested location.";
        } else if (result.status == NavigationStatus::REPLANNED) {
            feedback = "Had to replan the route due to obstacles, but successfully reached the destination.";
        } else {
            feedback = "Navigation failed: " + result.message;
        }

        // In a real system, this would go back to the VLA system
        RCLCPP_INFO(rclcpp::get_logger("VLA_Navigation"), "Navigation feedback: %s", feedback.c_str());
    }
};
```

## Human-Aware Navigation

### Socially-Aware Navigation Behaviors

```cpp
// human_aware_navigation.cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <people_msgs/msg/person.hpp>
#include <people_msgs/msg/people.hpp>
#include <social_navigation_layers/social_layer.hpp>

class HumanAwareNavigation : public rclcpp::Node
{
public:
    HumanAwareNavigation()
        : Node("human_aware_navigation")
    {
        // Subscriptions
        people_sub_ = this->create_subscription<people_msgs::msg::People>(
            "people", 10,
            std::bind(&HumanAwareNavigation::peopleCallback, this, std::placeholders::_1));

        // Parameters for human-aware navigation
        this->declare_parameter("personal_space_radius", 0.8);      // meters
        this->declare_parameter("social_zone_radius", 1.5);        // meters
        this->declare_parameter("comfortable_passing_distance", 0.6); // meters
        this->declare_parameter("eye_contact_distance", 2.0);      // meters
        this->declare_parameter("wait_for_passage_timeout", 5.0);  // seconds

        personal_space_radius_ = this->get_parameter("personal_space_radius").as_double();
        social_zone_radius_ = this->get_parameter("social_zone_radius").as_double();
        comfortable_passing_distance_ = this->get_parameter("comfortable_passing_distance").as_double();
        eye_contact_distance_ = this->get_parameter("eye_contact_distance").as_double();
        wait_for_passage_timeout_ = this->get_parameter("wait_for_passage_timeout").as_double();

        RCLCPP_INFO(this->get_logger(), "Human-Aware Navigation initialized");
    }

private:
    rclcpp::Subscription<people_msgs::msg::People>::SharedPtr people_sub_;

    // Human-aware navigation parameters
    double personal_space_radius_;
    double social_zone_radius_;
    double comfortable_passing_distance_;
    double eye_contact_distance_;
    double wait_for_passage_timeout_;

    // Human tracking
    std::map<int, PersonInfo> tracked_people_;
    rclcpp::Time last_update_time_;

    struct PersonInfo {
        geometry_msgs::msg::Point position;
        geometry_msgs::msg::Point velocity;
        rclcpp::Time last_seen;
        bool is_static;  // Whether person appears to be stationary
    };

    void peopleCallback(const people_msgs::msg::People::SharedPtr msg)
    {
        last_update_time_ = this->get_clock()->now();

        // Update tracked people
        for (const auto& person : msg->people) {
            PersonInfo person_info;
            person_info.position = person.position;
            person_info.velocity.x = person.velocity.x;
            person_info.velocity.y = person.velocity.y;
            person_info.velocity.z = person.velocity.z;
            person_info.last_seen = last_update_time_;
            person_info.is_static = (std::sqrt(person.velocity.x*person.velocity.x +
                                             person.velocity.y*person.velocity.y) < 0.1);

            tracked_people_[person.id] = person_info;
        }

        // Remove people not seen for a while
        auto it = tracked_people_.begin();
        while (it != tracked_people_.end()) {
            if ((last_update_time_ - it->second.last_seen).seconds() > 5.0) {
                it = tracked_people_.erase(it);
            } else {
                ++it;
            }
        }
    }

    double calculateSocialCost(const geometry_msgs::msg::Point& position) const
    {
        double total_cost = 0.0;

        for (const auto& person_pair : tracked_people_) {
            const auto& person = person_pair.second;

            double dx = position.x - person.position.x;
            double dy = position.y - person.position.y;
            double distance = std::sqrt(dx*dx + dy*dy);

            if (distance < social_zone_radius_) {
                // Higher cost as we get closer to personal space
                double normalized_distance = distance / personal_space_radius_;
                double cost = (normalized_distance < 1.0) ?
                             1000.0 :  // Very high cost in personal space
                             1.0 / (normalized_distance * normalized_distance);  // Inverse square falloff
                total_cost += cost;
            }
        }

        return total_cost;
    }

    bool shouldWaitForPerson(const geometry_msgs::msg::Pose& robot_pose,
                           const geometry_msgs::msg::Pose& target_pose) const
    {
        // Check if path to target intersects with person's space
        for (const auto& person_pair : tracked_people_) {
            const auto& person = person_pair.second;

            // Calculate if path intersects person's space
            double path_distance_to_person = calculateDistanceToLine(
                {robot_pose.position.x, robot_pose.position.y},
                {target_pose.position.x, target_pose.position.y},
                {person.position.x, person.position.y}
            );

            if (path_distance_to_person < comfortable_passing_distance_ && !person.is_static) {
                return true;
            }
        }

        return false;
    }

    double calculateDistanceToLine(const std::pair<double, double>& line_start,
                                 const std::pair<double, double>& line_end,
                                 const std::pair<double, double>& point) const
    {
        double A = point.first - line_start.first;
        double B = point.second - line_start.second;
        double C = line_end.first - line_start.first;
        double D = line_end.second - line_start.second;

        double dot = A * C + B * D;
        double len_sq = C * C + D * D;

        if (len_sq == 0) return std::sqrt(A*A + B*B);  // Line is actually a point

        double param = dot / len_sq;

        double xx, yy;
        if (param < 0) {
            xx = line_start.first;
            yy = line_start.second;
        } else if (param > 1) {
            xx = line_end.first;
            yy = line_end.second;
        } else {
            xx = line_start.first + param * C;
            yy = line_start.second + param * D;
        }

        double dx = point.first - xx;
        double dy = point.second - yy;
        return std::sqrt(dx*dx + dy*dy);
    }

    // Human-aware path planning interface
    class HumanAwarePathPlanner
    {
    public:
        HumanAwarePathPlanner(double personal_space_radius, double social_zone_radius)
            : personal_space_radius_(personal_space_radius),
              social_zone_radius_(social_zone_radius) {}

        PathPlan PlanPathWithHumans(const Pose& start,
                                  const Pose& goal,
                                  const std::map<int, PersonInfo>& people) const
        {
            // Create cost map that includes human-aware costs
            auto cost_map = CreateHumanAwareCostMap(people);

            // Plan path using the human-aware cost map
            // This would typically use a modified A* or Dijkstra's algorithm
            // that considers the additional social costs

            // For now, return a basic path with human considerations
            PathPlan path_plan = BasicPathPlanner::PlanPath(start, goal, cost_map);

            // Post-process path to ensure human-aware behavior
            path_plan = PostProcessForHumans(path_plan, people);

            return path_plan;
        }

    private:
        double personal_space_radius_;
        double social_zone_radius_;

        CostMap CreateHumanAwareCostMap(const std::map<int, PersonInfo>& people) const
        {
            // Create a cost map that increases costs near humans
            CostMap cost_map;

            // Add costs for each person's space
            for (const auto& person_pair : people) {
                const auto& person = person_pair.second;

                // Create circular cost influence around person
                AddCircularCostInfluence(cost_map, person.position, social_zone_radius_, 10.0);
            }

            return cost_map;
        }

        void AddCircularCostInfluence(CostMap& cost_map,
                                    const geometry_msgs::msg::Point& center,
                                    double radius,
                                    double max_cost) const
        {
            // Add cost influence in a circular area around the center
            // This is a simplified implementation
            int grid_size = 100;  // 100x100 grid
            double resolution = 0.1;  // 10cm resolution

            for (int x = 0; x < grid_size; ++x) {
                for (int y = 0; y < grid_size; ++y) {
                    double world_x = center.x - (grid_size/2) * resolution + x * resolution;
                    double world_y = center.y - (grid_size/2) * resolution + y * resolution;

                    double dx = world_x - center.x;
                    double dy = world_y - center.y;
                    double distance = std::sqrt(dx*dx + dy*dy);

                    if (distance <= radius) {
                        double normalized_distance = distance / radius;
                        double cost = max_cost * (1.0 - normalized_distance);  // Higher cost closer to center

                        // Add to cost map (implementation depends on specific cost map structure)
                        cost_map.AddCost(x, y, cost);
                    }
                }
            }
        }

        PathPlan PostProcessForHumans(PathPlan path_plan,
                                    const std::map<int, PersonInfo>& people) const
        {
            // Post-process the path to ensure appropriate behavior around humans
            // This might involve:
            // - Adding waypoints to go around people
            // - Smoothing path to maintain appropriate distances
            // - Adding temporary stops for social interaction

            // For now, just return the original path
            return path_plan;
        }
    };
};
```

This comprehensive navigation behaviors implementation provides:

1. **ROS 2 Action Integration**: Complete action server and client implementations for navigation
2. **Behavior Trees**: Complex decision-making for navigation scenarios
3. **Humanoid-Specific Behaviors**: Balance-aware navigation for bipedal robots
4. **Semantic Navigation**: Integration with vision-language systems
5. **Human-Aware Navigation**: Socially-aware navigation behaviors

The implementation is designed to work with vision-language-action systems, enabling humanoid robots to understand and execute navigation commands that consider both spatial relationships and social contexts.