// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'ROS 2 Fundamentals',
      items: [
        'ros2-fundamentals/chapter-1-fundamentals/index',
        'ros2-fundamentals/chapter-1-fundamentals/nodes-topics-services',
        'ros2-fundamentals/chapter-1-fundamentals/publisher-subscriber-model',
      ],
    },
    {
      type: 'category',
      label: 'AI Agents with rclpy',
      items: [
        'ros2-fundamentals/chapter-2-ai-agents/index',
        'ros2-fundamentals/chapter-2-ai-agents/rclpy-integration',
        'ros2-fundamentals/chapter-2-ai-agents/ai-to-robot-control',
      ],
    },
    {
      type: 'category',
      label: 'Humanoid Modeling with URDF',
      items: [
        'ros2-fundamentals/chapter-3-urdf-modeling/index',
        'ros2-fundamentals/chapter-3-urdf-modeling/links-joints-frames',
        'ros2-fundamentals/chapter-3-urdf-modeling/visual-collision-models',
      ],
    },
    {
      type: 'category',
      label: 'The Digital Twin (Gazebo & Unity)',
      items: [
        'digital-twin/index',
        {
          type: 'category',
          label: 'Physics Simulation with Gazebo',
          items: [
            'digital-twin/chapter-1-physics-sim/index',
            'digital-twin/chapter-1-physics-sim/gravity-collisions-environments',
            'digital-twin/chapter-1-physics-sim/simulation-realism-validation',
          ],
        },
        {
          type: 'category',
          label: 'Visual & Interaction Simulation with Unity',
          items: [
            'digital-twin/chapter-2-visual-interaction/index',
            'digital-twin/chapter-2-visual-interaction/high-fidelity-rendering',
            'digital-twin/chapter-2-visual-interaction/human-robot-interaction',
            'digital-twin/chapter-2-visual-interaction/unity-vs-gazebo-roles',
          ],
        },
        {
          type: 'category',
          label: 'Sensor Simulation',
          items: [
            'digital-twin/chapter-3-sensor-sim/index',
            'digital-twin/chapter-3-sensor-sim/lidar-depth-cameras-imus',
            'digital-twin/chapter-3-sensor-sim/noise-real-world-approximation',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'ai-robot-brain/index',
        {
          type: 'category',
          label: 'Synthetic Data Generation with Isaac Sim',
          items: [
            'ai-robot-brain/chapter-1-synthetic-data/index',
            'ai-robot-brain/chapter-1-synthetic-data/isaac-sim-setup',
            'ai-robot-brain/chapter-1-synthetic-data/rgb-depth-segmentation-generation',
          ],
        },
        {
          type: 'category',
          label: 'VSLAM Pipeline Implementation',
          items: [
            'ai-robot-brain/chapter-2-vslam/index',
          ],
        },
        {
          type: 'category',
          label: 'Navigation Planning with Nav2',
          items: [
            'ai-robot-brain/chapter-3-navigation/index',
          ],
        },
      ],
    },
  ],
};

module.exports = sidebars;