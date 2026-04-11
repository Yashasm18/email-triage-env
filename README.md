---
title: Email Triage Agentic Env
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
license: apache-2.0
short_description: Agentic Benchmark for Enterprise Security & Data Governance.
pinned: false
tags:
  - openenv
  - agents
  - meta-pytorch-hackathon
  - reinforcement-learning
tasks:
  - id: email-classification
    type: text-classification
    grader: grader.grade
  - id: urgency-detection
    type: text-classification
    grader: grader.grade
  - id: spam-filtering
    type: text-classification
    grader: grader.grade
---

# 📧 Intelligent Email Triage OpenEnv
**An Autonomous Agentic Framework for High-Precision Enterprise Governance and Security Routing**

![Validation Status](https://huggingface.co/spaces/souller/email-triage-env/resolve/main/assets/validation.png)

> **Phase 2 Status:** Infrastructure Synchronized & Fully Validated (5/5 Checks). Optimized for the Meta OpenEnv Deep Validator.

---

## 🚀 1. Executive Summary
In modern enterprise ecosystems, manual triage is the primary bottleneck for operational efficiency. **Intelligent Email Triage (IET)** is a high-fidelity Reinforcement Learning environment designed to evaluate Large Language Model (LLM) agents on their ability to act as an autonomous **First-Line Digital Responder**.

IET benchmarks an agent's capability to process unstructured natural language, perform high-precision risk assessment, and execute strategic routing across internal corporate departments (Security, Legal, Engineering) while maintaining professional corporate "Tone of Voice."

---

## 🗺️ 2. System Architecture: The Sentinel Reasoning Loop
We employ a **Dual-Stage Heuristic-Guided Loop**. To prevent hallucinations in high-stakes routing, our architecture separates initial "Creative Drafting" from "Strategic Validation."

### Cognitive Pipeline:
1. **Chain-of-Thought Perception:** The agent analyzes the email for hidden intent and technical severity.
2. **Drafting Layer:** A triage action is proposed in a strictly structured JSON format.
3. **Self-Correction:** A secondary "Quality Critic" audit reviews the draft for policy alignment.
4. **Strategic Execution:** The final validated action is committed to the environment.

```mermaid
graph TD
    A[Incoming Corporate Signal] --> B[🛡️ Team Soul Agent]
    B --> C[📝 Draft Triage Action]
    C --> D[🔍 Self-Correction Critic]
    D -- "Logic Gap" --> B
    D -- "Validated" --> E[🏁 Strategic Routing]
    E --> F[📊 Reward Function]
---

## 🚀 8. Setup & Installation

### Prerequisites
- Docker installed and running.
- Python 3.10+
- `openenv-core` library (`pip install openenv-core`)

### Local Deployment
To run the AntiGravity environment locally for testing:
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yashasm18/email-triage-env.git
   cd email-triage-env
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
.
├── assets/             # Technical validation & UI screenshots
├── outputs/            # Placeholder for agent execution logs
├── server/             # Core logic (FastAPI)
│   ├── app.py          # Entry point with /tasks support
│   └── my_env_environment.py  # Expert-grade RL environment
├── grader.py           # Multi-factor reward calculation engine
├── inference.py        # Dual-Agent Self-Correction logic
├── openenv.yaml        # Spec-compliant environment config
└── requirements.txt    # Dependency manifest
