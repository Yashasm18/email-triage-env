---
title: AntiGravity Email Triage
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
license: apache-2.0
short_description: High-Precision Agentic Benchmark for Enterprise Security Triage.
pinned: false
tags:
  - openenv
  - agents
  - meta-pytorch-hackathon
  - reinforcement-learning
  - research
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

# 🚀 AntiGravity: Enterprise Governance & Security Triage
**An Autonomous Agentic Benchmark for High-Stakes Corporate Incident Management**

![Validation Status](https://huggingface.co/spaces/souller/email-triage-env/resolve/main/assets/validation.png)

> **Phase 1 Status:** Successfully Validated (5/5 Checks). Fully compliant with Meta OpenEnv Spec v1.0.

---

## 📖 1. Abstract & Project Philosophy
In modern enterprise environments, the "signal-to-noise" ratio in communication channels is at an all-time high. Manual triage of security alerts and data privacy requests costs companies millions in operational latency. 

**AntiGravity** (named after the legendary Python `import antigravity` easter egg) is engineered to "lift" the cognitive weight of triage off human operators. It is not just a tool; it is a **Reinforcement Learning (RL) Benchmark** designed to evaluate an LLM agent's ability to act as an autonomous **Incident Commander** and **Data Governance Officer**.

---

## 🗺️ 2. System Architecture: The AntiGravity Protocol
We utilize a **Heuristic-Guided Agentic Loop**. Standard LLM calls often suffer from hallucinations in high-pressure scenarios (routing a security threat to marketing). Our architecture employs a dual-stage **Draft-Critic** model to ensure strategic alignment.

### 🧠 Cognitive Reasoning Loop
1. **Perception:** The agent ingest raw enterprise signals.
2. **Chain-of-Thought (CoT):** The agent performs an internal audit of technical severity and legal risk.
3. **Drafting:** A triage action is proposed in structured JSON.
4. **Criticism:** A secondary "Quality Control" agent reviews the draft for policy violations.
5. **Execution:** The refined action is committed to the environment.

```mermaid
flowchart TD
    A[📧 Incoming Enterprise Message] --> B{🛡️ Primary Agent}
    B -->|Chain-of-Thought Reasoning| C[📝 Proposed Triage Action]
    C --> D{🔍 Quality Critic Agent}
    D -- "Logic Gap Detected" --> B
    D -- "Validated Policy" --> E[🏁 Strategic Execution]
    E --> F[📊 Reward Function]
# Clone the repository
git clone https://github.com/Yashasm18/email-triage-env.git
cd email-triage-env

# Build and run the local container
docker build -t antigravity-env .
docker run -p 7860:7860 antigravity-env
.
├── assets/             # Visual validation & UI documentation
├── outputs/            # Execution logs and reward history
├── server/             # Core Infrastructure (FastAPI)
│   ├── app.py          # Entry point with /tasks & task_id support
│   └── my_env_environment.py  # Expert-grade RL environment
├── grader.py           # Multi-factor reward calculation engine
├── inference.py        # AntiGravity Dual-Agent Logic
├── openenv.yaml        # Spec-compliant environment config
└── requirements.txt    # Dependency manifest
@benchmark{teamsoul_antigravity_2026,
  author = {Team Soul (Yashasm18)},
  title = {AntiGravity: An Agentic Benchmark for Enterprise Governance},
  year = {2026},
  publisher = {Hugging Face},
  url = {https://huggingface.co/spaces/souller/email-triage-env}
}
