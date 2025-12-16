---
id: 1
title: Update Constitution
stage: constitution
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Claude Code
command: /sp.constitution
labels: [constitution,documentation,setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

```
/sp.constitution

Project:
AI-Native Physical AI & Humanoid Robotics Book with RAG Chatbot

Purpose:
Create and deploy an AI-native educational book on Physical AI and Humanoid Robotics using Docusaurus and GitHub Pages, with an embedded RAG chatbot answering questions strictly from book content and user-selected text.

Core Principles:
- Accuracy from primary and official sources
- Clarity for CS/Software Engineering students
- Reproducibility (code, specs, simulations)
- Simulation-first Physical AI development
- Embodied Intelligence (perception → reasoning → action)

Tech Stack:
- Docs: Docusaurus
- Specs: Spec-Kit Plus
- Authoring: Claude Code
- Robotics: ROS 2, Gazebo, Unity, NVIDIA Isaac Sim, Nav2
- RAG: FastAPI, OpenAI Agents/ChatKit, Neon Postgres, Qdrant
- Voice: OpenAI Whisper

Content Scope:
- ROS 2 (nodes, topics, services, URDF, rclpy)
- Digital Twins (physics, sensors, simulation realism)
- AI-Robot Brain (Isaac Sim, VSLAM, navigation)
- Vision-Language-Action (LLM → ROS actions, voice commands)
- Capstone: Autonomous humanoid in simulation

Standards:
- All factual claims must be traceable
- Citation style: APA
- ≥60% official or peer-reviewed sources
- No hallucinated content
- Deterministic LLM-to-robot action pipelines

RAG Rules:
- Answer only from indexed book content
- Support user-selected-text-only answers
- Return "Not found in provided text" if unsupported
- Cite chapter or section in responses

Structure & Writing:
- Modular, chapter-based
- Each chapter: concepts, architecture, specs/code, simulation
- Clarity target: Flesch-Kincaid Grade 10–12

Safety & Ethics:
- Simulation before real-world deployment
- Explicit safety limits and failure modes

Success Criteria:
- Book live on GitHub Pages
- RAG chatbot works as specified
- Reproducible simulations and code
- Zero uncited or fabricated claims
```

## Response snapshot

Updated the project constitution with specific details for the AI-Native Physical AI & Humanoid Robotics Book project. The new constitution includes core principles around accuracy, clarity, reproducibility, simulation-first development, and embodied intelligence. It also incorporates tech stack integration, content standards, RAG system rules, and safety/ethics standards.

## Outcome

- ✅ Impact: Created comprehensive project constitution with specific principles and standards
- 🧪 Tests: No tests required for constitution update
- 📁 Files: Updated .specify/memory/constitution.md with project-specific content
- 🔁 Next prompts: Ready to proceed with project planning and specification
- 🧠 Reflection: Constitution now properly reflects the project requirements and constraints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Proceed with project planning based on new constitution