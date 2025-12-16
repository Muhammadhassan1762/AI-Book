<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 → 1.1.0
Modified principles: [PRINCIPLE_1_NAME] → Accuracy and Traceability, [PRINCIPLE_2_NAME] → Clarity for Students, [PRINCIPLE_3_NAME] → Reproducibility, [PRINCIPLE_4_NAME] → Simulation-First Development, [PRINCIPLE_5_NAME] → Embodied Intelligence
Added sections: Tech Stack Principles, Content Standards, RAG Rules, Safety and Ethics
Removed sections: None
Templates requiring updates: ✅ Updated
Follow-up TODOs: None
-->
# AI-Native Physical AI & Humanoid Robotics Book Constitution

## Core Principles

### I. Accuracy and Traceability
All factual claims must be traceable to primary and official sources; ≥60% of content must come from official or peer-reviewed sources; No hallucinated content allowed; APA citation style required for all references

### II. Clarity for Students
Content must be clear and accessible for CS/Software Engineering students; Clarity target: Flesch-Kincaid Grade 10–12; Modular, chapter-based structure with concepts, architecture, specs/code, and simulation in each chapter

### III. Reproducibility
All code, specifications, and simulations must be reproducible; Deterministic LLM-to-robot action pipelines required; Code and specs must work consistently across environments

### IV. Simulation-First Physical AI Development
Prioritize simulation before real-world deployment; Focus on digital twins with physics, sensors, and simulation realism; Use simulation for testing before physical implementation

### V. Embodied Intelligence
Emphasize perception → reasoning → action pipeline; Develop AI-Robot brain with Isaac Sim, VSLAM, navigation; Integrate Vision-Language-Action for LLM-to-ROS actions and voice commands

### VI. Tech Stack Integration
Use Docusaurus for documentation, Spec-Kit Plus for specifications, ROS 2 for robotics, FastAPI for RAG backend, OpenAI Agents/ChatKit for AI capabilities, with Neon Postgres and Qdrant for vector storage

## Content Standards and Requirements

- All factual claims must be traceable to credible sources
- Citation style: APA format
- At least 60% of content must come from official or peer-reviewed sources
- No fabricated or hallucinated content
- Deterministic LLM-to-robot action pipelines
- Content scope includes ROS 2, Digital Twins, AI-Robot Brain, Vision-Language-Action, and capstone autonomous humanoid projects

## RAG System Rules

- RAG chatbot must answer only from indexed book content
- Support user-selected-text-only answers
- Return "Not found in provided text" if question cannot be answered from provided content
- All responses must cite the relevant chapter or section
- Strict adherence to content boundaries - no external knowledge injection

## Safety and Ethics Standards

- Simulation before real-world deployment is mandatory
- Explicit safety limits and failure modes must be documented
- Ethical considerations for AI and robotics applications must be addressed
- Clear guidelines for responsible AI development and deployment

## Development Workflow

- Create and deploy using Docusaurus and GitHub Pages
- Use Claude Code for authoring assistance
- Follow modular, chapter-based structure
- Each chapter must include concepts, architecture, specs/code, and simulation
- Maintain simulation-first approach throughout development

## Governance

This constitution governs all aspects of the AI-Native Physical AI & Humanoid Robotics Book project. All development, content creation, and deployment activities must comply with these principles. Changes to this constitution require explicit approval and documentation of the rationale. All team members must verify compliance with these principles during reviews and development.

**Version**: 1.1.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15