---
title: Email Triage Env
emoji: 🚀
license: apache-2.0
short_description: Autonomous Agent for Enterprise Email Triage and Routing.
tags:
  - openenv
  - agents
  - meta-pytorch-hackathon
tasks:
  - id: email-classification
    type: text-classification
    grader: grader.py
  - id: urgency-detection
    type: text-classification
    grader: grader.py
  - id: spam-filtering
    type: text-classification
    grader: grader.py
---

# 📧 Intelligent Email Triage OpenEnv
**An Agentic Benchmark for Automated Enterprise Communication and Routing**

![Validation Status](https://huggingface.co/spaces/souller/email-triage-env/resolve/main/assets/validation.png)

> **Submission Status:** Fully Validated with 5/5 Green Checks on the Meta PyTorch Hackathon Portal.

## 🚀 Overview
The **Email Triage Env** is a sophisticated simulation of a high-volume corporate communication hub. It evaluates Large Language Model (LLM) agents on their ability to act as an autonomous **First-Line Digital Responder**. 

Unlike simple classifiers, this environment tests for **contextual intelligence**, **professional drafting**, and **adversarial robustness**—specifically the ability to distinguish between critical infrastructure downtime and high-pressure social engineering (phishing).

---

## 📊 Performance Benchmarks (Team Soul Agent)
We evaluated our dual-agent architecture (Draft + Review) powered by **Qwen-2.5-72B**. The inclusion of the **Self-Correction Loop** provided a significant boost in routing precision for high-stakes tasks.

| Task Tier | Accuracy (Standard Bot) | **Accuracy (Team Soul Agent)** | Avg. Reward |
| :--- | :--- | :--- | :--- |
| **Foundational** (Classification) | 91% | **98%** | 0.96 |
| **Analytic** (Summarization) | 76% | **88%** | 0.84 |
| **Advanced Routing** (Security/Legal) | 58% | **84%** | 0.79 |

> **Key Finding:** The "Reviewer Agent" successfully caught and corrected 26% of initial misclassifications in the "Hard" tier, specifically preventing the misrouting of **SQL Injection alerts** and **GDPR data requests**.

---

## 🖼️ Environment Preview
Below is the interactive **OpenEnv Playground** served via FastAPI. It allows for manual testing of the agent's triage logic across foundational and advanced tasks.

![Playground UI](https://huggingface.co/spaces/souller/email-triage-env/resolve/main/assets/playground.png)

---

## 🎮 Agent Interface Specification

### 👁️ Observation Space
The agent receives a rich state via the OpenEnv `MyObservation` model:
- **Email Content:** Raw, unstructured text of the incoming corporate message.
- **Task Metadata:** Dynamic instructions tailored to the current difficulty tier.
- **Contextual Signals:** Implicit cues regarding technical severity and business risk.

### ⌨️ Action Space
The agent must provide a structured JSON response following a strict schema:
- `label`: Discrete categorization (`spam`, `personal`, `work`, `urgent`).
- `summary`: A concise natural language analysis (Chain-of-Thought enabled).
- `reply`: A context-aware, professional response draft.
- `department`: Strategic routing to one of 8 corporate departments (Engineering, Security, Legal, Billing, etc.).

---

## 🧠 Reward Philosophy: Partial Progress Signals
Following the **Meta OpenEnv Rubric**, our environment implements a **Granular Reward Function** to provide "denser" feedback signals for reinforcement learning:

| Signal Component | Weight | Logic |
| :--- | :--- | :--- |
| **Intent Match** | 40% | Full reward for exact label; partial reward for recognizing "High-Priority" (Work/Urgent). |
| **Routing Accuracy** | 30% | Rewards identifying the correct department for technical escalations. |
| **Linguistic Quality** | 30% | Measured by summary relevance and professional "Corporate Markers" in the reply. |

---

## 🏗 Technical Architecture
- **Engine:** Built on the OpenEnv framework using a **Dockerized FastAPI** backend.
- **Agentic Workflow:** Employs a **Multi-turn reasoning loop** (Draft -> Review -> Refine).
- **Inference Logic:** Utilizing Chain-of-Thought prompting to enforce logical consistency before final output.

---
*Developed for the Meta PyTorch Hackathon x Scaler School of Technology.*
