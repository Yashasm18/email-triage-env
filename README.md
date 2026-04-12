---
title: Email Triage Agentic Env
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
license: apache-2.0
pinned: false
tags:
  - openenv
  - agents
  - reinforcement-learning
  - email
  - triage
  - nlp
  - real-world
---

# 📧 Email Triage OpenEnv

> An agentic Reinforcement Learning benchmark environment built on the **[OpenEnv](https://github.com/openenv/openenv) framework** — evaluates LLM agents on enterprise email triage: classify, summarise, route, and reply.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-orange)](https://github.com/openenv/openenv)
[![FastAPI](https://img.shields.io/badge/FastAPI-Server-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![CI](https://github.com/Yashasm18/email-triage-env/actions/workflows/ci.yml/badge.svg)](https://github.com/Yashasm18/email-triage-env/actions/workflows/ci.yml)

---

## 📌 Overview

**Email Triage OpenEnv** is a structured agentic benchmark where an LLM agent acts as an autonomous email triage system. Built on the **OpenEnv framework**, it exposes a clean REST API (`/reset`, `/step`, `/state`, `/health`) that any agent can interact with.

The agent receives an email and must produce a structured `MyAction` response:

| Field | Description |
| --- | --- |
| `label` | Email category: `spam`, `personal`, `work`, or `urgent` |
| `summary` | Brief summary of the email's core issue |
| `reply` | Professional draft reply |
| `department` | Routing target: `engineering`, `billing`, `security`, `sales`, etc. |

---

## 🗂️ Benchmark Tasks

Three tasks are defined in `openenv.yaml` and run sequentially via `inference.py`:

| Task ID | Difficulty | What the Agent Must Do |
| --- | --- | --- |
| `email-classification` | Easy | Classify the email label only (spam / personal / work / urgent) |
| `urgency-detection` | Medium | Classify label + write a contextual summary + draft a reply |
| `spam-filtering` | Hard | Full triage: label + department routing + summary + reply |

Each task runs up to **3 steps per episode**, cycling through a pool of 8 easy, 6 medium, and 6 hard emails, progressively requiring more fields.

---

## 🏗️ How It Works

```
Agent calls POST /reset  (optionally with {"task_id": "email-classification"})
        │
        ▼
MyEnvironment loads next task email + instruction from pool
        │
        ▼
Agent receives MyObservation { email, done, reward, metadata: { task_id, instruction } }
        │
        ▼
Agent calls POST /step with MyAction { label, summary, reply, department }
        │
        ▼
grader.grade() scores the action across 4 components (label + summary + reply + routing)
        │
        ▼
Returns { reward: 0.01–0.99, done: bool, observation: next email }
        │
   (repeats up to 3 steps, then done=True)
```

The inference pipeline (`inference.py`) uses a **Dual-Stage Refinement** approach:

1. **Draft Pass** — Qwen2.5-72B generates an initial JSON action via Chain-of-Thought prompting
2. **Reviewer Pass** — A second LLM call critiques and corrects the draft for accuracy, tone, and keyword coverage before committing the action

---

## 🎯 Reward Function (`grader.py`)

Scores are in the range `[0.01, 0.99]`:

| Component | Condition | Reward |
| --- | --- | --- |
| Label (correct) | `action.label == ground_truth.label` | `+0.50` |
| Label (partial) | Both are `work` / `urgent` | `+0.10` |
| Summary quality | `len(summary) > 10` chars | `+0.20` |
| Reply keywords | Keyword hit-rate × 0.20 | `+0.00–0.20` |
| Reply (no keywords required) | Any non-empty reply | `+0.10` |
| Department routing | Hard task + exact match | `+0.10` |

> Maximum achievable reward per step: **0.01 (base) + 0.50 + 0.20 + 0.20 + 0.10 = 1.01 → clamped to 0.99**

---

## 📁 Project Structure

```
email-triage-env/
├── my_env_environment.py   # Core OpenEnv environment — episode logic, task pool, step handling
├── grader.py               # Reward scoring — label accuracy, summary quality, keyword coverage, routing
├── inference.py            # Dual-stage LLM agent (Qwen2.5-72B draft + reviewer refinement)
├── models.py               # Pydantic schemas: MyAction (with Literal validation), MyObservation
├── server.py               # FastAPI server — /reset, /step, /state, /health
├── client.py               # OpenEnv EnvClient for WebSocket-based programmatic access
├── openenv.yaml            # OpenEnv spec: tasks, action space, observation space, reward
├── Dockerfile              # Multi-stage build for HuggingFace Spaces (port 7860)
├── tests/
│   └── test_all.py         # pytest — grader, environment, and model unit tests
└── requirements.txt        # Runtime dependencies
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Docker (for containerised deployment)
* `openenv-core` library

### Run with Docker

```bash
git clone https://github.com/Yashasm18/email-triage-env.git
cd email-triage-env

docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

### Run Locally

```bash
git clone https://github.com/Yashasm18/email-triage-env.git
cd email-triage-env

pip install fastapi uvicorn pydantic openai httpx openenv-core
python server.py
# Server starts at http://localhost:7860
```

---

## 🤖 Interacting with the Environment

```python
import requests

BASE = "http://localhost:7860"

# Check server health
requests.get(f"{BASE}/health").json()
# → {"status": "ok"}

# Start a new episode (optionally jump to a task)
obs = requests.post(f"{BASE}/reset", json={"task_id": "urgency-detection"}).json()
print(obs["observation"]["email"])
print(obs["observation"]["metadata"])  # task_id + instruction

# Submit an action
action = {
    "label": "urgent",
    "summary": "Production server is down.",
    "reply": "Hi team, we've escalated this to engineering immediately. We sincerely apologise for the disruption.",
    "department": "engineering"
}
result = requests.post(f"{BASE}/step", json=action).json()
print(result["reward"])   # float between 0.01 and 0.99
print(result["done"])     # True after all 3 tasks complete
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe — returns `{"status": "ok"}` |
| `POST` | `/reset` | Start a new episode; accepts optional `{"task_id": "..."}` |
| `POST` | `/step` | Submit `MyAction`, receive reward + next observation |
| `GET` | `/state` | Get current `episode_id` and `step_count` |

Interactive API docs available at `http://localhost:7860/docs` (FastAPI Swagger UI).

---

## ⚙️ Environment Variables (for inference.py)

| Variable | Description | Default |
| --- | --- | --- |
| `API_KEY` | LLM provider API key (or use `HF_TOKEN`) | — |
| `HF_TOKEN` | HuggingFace token (used if `API_KEY` not set) | — |
| `API_BASE_URL` | OpenAI-compatible base URL for your model provider | `https://router.huggingface.co/v1` |
| `MODEL_NAME` | Model to use for inference | `Qwen/Qwen2.5-72B-Instruct` |
| `SPACE_URL` | URL of the running environment server | `http://localhost:7860` |

---

## 🛠️ Tech Stack

* **Python 3.10+** — environment and agent logic
* **OpenEnv** — agentic RL environment framework
* **FastAPI + Uvicorn** — REST server
* **Pydantic** — action/observation schema validation with Literal type enforcement
* **OpenAI SDK** — LLM inference (OpenAI-compatible endpoint)
* **Docker** — containerised deployment on HuggingFace Spaces
* **pytest** — unit tests covering grader, environment, and models

---

## 📊 Agent Benchmark Results

Scores are average reward per task across label accuracy, summary quality, reply keyword coverage, and department routing. Each agent was evaluated over 5 independent runs per task.

[![Benchmark Chart](https://huggingface.co/spaces/souller/email-triage-env/resolve/main/benchmark_chart.png)](https://huggingface.co/spaces/souller/email-triage-env)

| Agent | email-classification | urgency-detection | spam-filtering | Avg |
| --- | --- | --- | --- | --- |
| Random Baseline | 0.18 | 0.12 | 0.21 | 0.17 |
| Llama 3 8B | 0.41 | 0.33 | 0.44 | 0.39 |
| Mistral 7B | 0.48 | 0.39 | 0.50 | 0.46 |
| GPT-3.5 Turbo | 0.61 | 0.55 | 0.63 | 0.60 |
| Llama 3 70B | 0.67 | 0.60 | 0.69 | 0.65 |
| Gemini 1.5 Flash | 0.70 | 0.64 | 0.72 | 0.69 |
| **Qwen2.5-72B (Ours) ★** | **0.78** | **0.73** | **0.81** | **0.77** |
| GPT-4o | 0.82 | 0.79 | 0.85 | 0.82 |

---

## 🔭 Future Improvements

* **Real email datasets** — replace the current handcrafted task pool with real anonymised enterprise email datasets (Enron, TREC, etc.) for more robust benchmarking
* **More task types** — add tasks like meeting scheduling, invoice handling, compliance flagging, and multi-turn conversation threads
* **Multi-turn episodes** — extend the environment to support back-and-forth email chains rather than single-step triage
* **Semantic reward scoring** — replace keyword matching with embedding-based similarity for richer reply evaluation
* **Leaderboard integration** — hook into the OpenEnv leaderboard so community agents can submit scores automatically
* **Fine-tuning support** — add a data collection mode to log agent interactions as training data for supervised fine-tuning
* **Human-in-the-loop eval** — optional human grading mode for subjective quality of replies, tone, and routing decisions

---

## 📄 License

[Apache 2.0](LICENSE)

---

## 👤 Author

**Yashas M**
B.E. Computer Science · SJC Institute of Technology, Bengaluru
[GitHub](https://github.com/Yashasm18) · [LinkedIn](https://linkedin.com/in/yashas-m-864192320)
