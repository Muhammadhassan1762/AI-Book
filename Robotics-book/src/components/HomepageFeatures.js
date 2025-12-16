import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

const FeatureList = [
  {
    title: 'ROS 2 Fundamentals',
    description: (
      <>
        Learn the core concepts of ROS 2 including nodes, topics, services, and the publisher-subscriber model.
      </>
    ),
  },
  {
    title: 'AI Integration',
    description: (
      <>
        Connect AI agents with robot controllers using rclpy, bridging decision-making with robot control.
      </>
    ),
  },
  {
    title: 'Advanced Robotics',
    description: (
      <>
        Master digital twins, NVIDIA Isaac ecosystem, and vision-language-action systems for humanoid robots.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}