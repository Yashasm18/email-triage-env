---
title: Email Triage Env
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
license: apache-2.0
short_description: Intelligent Agentic Workflow for Autonomous Enterprise Email Triage.
pinned: false
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

## 🚀 Overview
The **Email Triage Env** is a sophisticated simulation of a high-volume corporate communication hub. It evaluates Large Language Model (LLM) agents on their ability to act as an autonomous **First-Line Digital Responder**. 

Unlike simple classifiers, this environment tests for **contextual intelligence**, **professional drafting**, and **adversarial robustness**—specifically the ability to distinguish between critical infrastructure downtime and high-pressure social engineering (phishing).

---

## 🎮 Agent Interface Specification

### 👁️ Observation Space
The agent receives a rich state via the OpenEnv `MyObservation` model, including:
- **Email Content:** Raw, unstructured text of the incoming message.
- **Task Metadata:** Dynamic instructions tailored to the current difficulty tier.

### ⌨️ Action Space
The agent must provide a structured JSON response following a strict schema:
- `label`: Discrete categorization (`spam`, `personal`, `work`, `urgent`).
- `summary`: A concise natural language analysis of the sender's intent.
- `reply`: A context-aware, professional response draft.
- `department`: Strategic routing to one of 8 corporate departments (Engineering, Security, Legal, Billing, etc.).

---

## 🛠 The 3-Tier Benchmark
1. **email-classification (Foundational):** Intent Alignment and zero-shot categorization.
2. **urgency-detection (Analytic):** Contextual synthesis and professional tone maintenance.
3. **spam-filtering (Advanced Routing):** Enterprise logic involving GDPR and Security threats.

---

## 🧠 Reward Philosophy: Partial Progress Signals
Following the Meta rubric, we implement a **Granular Reward Function**:
- **Intent Match (40%):** Rewards label accuracy.
- **Routing Accuracy (30%):** Rewards identifying the correct technical department.
- **Linguistic Quality (30%):** Rewards professional markers and summary depth.

---
*Developed for the Meta PyTorch Hackathon x Scaler School of Technology.*
