---
title: Email Triage Env
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
**A High-Precision Agentic Benchmark for Enterprise Governance and Security Routing**

![Validation Status](https://huggingface.co/spaces/souller/email-triage-env/resolve/main/assets/validation.png)

> **Phase 1 Validation:** Passed with 5/5 Green Checks. Verified on Meta PyTorch Hackathon Portal.

## 🚀 Overview
The **Email Triage Env** is a sophisticated simulation of a high-pressure corporate communication hub. It evaluates Large Language Model (LLM) agents on their capacity to act as autonomous **Incident Commanders** and **Data Privacy Officers**.

The benchmark focuses on three critical enterprise pillars:
1. **Security Triage:** Distinguishing between social engineering and technical alerts.
2. **Regulatory Compliance:** Identifying high-stakes GDPR and legal requests.
3. **SRE Contextualization:** Synthesizing technical downtime reports for rapid engineering escalation.

---

## 🗺️ System Architecture: Dual-Agent Logic
We employ a **Heuristic-Guided Agentic Loop**. The system utilizes a Primary Agent for initial Chain-of-Thought synthesis and a Secondary "Critic" Agent for quality assurance before final routing.

```mermaid
flowchart TD
    A[📧 Incoming Enterprise Message] --> B{🛡️ Primary Agent}
    B -->|Chain-of-Thought Reasoning| C[📝 Draft Triage Action]
    C --> D{🔍 Quality Critic Agent}
    D -- "Inconsistencies Found" --> B
    D -- "Validated" --> E[🏁 Strategic Action]
    E --> F[📊 Reward Function]
