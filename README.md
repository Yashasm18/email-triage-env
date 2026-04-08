# 📧 Intelligent Email Triage OpenEnv

## 🚀 Overview
The **Email Triage Env** is a sophisticated simulation of a high-volume corporate communication hub. This environment evaluates Large Language Model (LLM) agents on their ability to act as a **first-line digital responder**.

It tests for **contextual intelligence**, **professional drafting**, and **adversarial detection** (distinguishing between urgent technical issues and high-pressure phishing attempts).

---

## 🛠 The 3-Tier Benchmark
1. **`email-classification` (Foundational):** categorizing intent into Spam, Personal, Work, or Urgent with zero-shot accuracy.
2. **`urgency-detection` (Analytic):** measuring technical downtime summarization and professional response drafting.
3. **`spam-filtering` (Advanced Routing):** the "Hard" tier. Identifying internal departments (Security, Legal, Billing) based on nuanced clues like IP logs or GDPR Article 15 requests.

---

## 🧠 Technical Architecture
- **Environment Logic:** Python-based stateful inbox simulation.
- **Granular Reward System:** Multi-factor rewards for label accuracy, professional tone, and routing precision.
- **Agentic Workflow:** Enforces strict JSON output schemas for downstream business automation.

---
*Developed for the Meta PyTorch Hackathon x Scaler School of Technology.*
