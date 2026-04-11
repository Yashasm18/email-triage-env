# 📧 Email Triage OpenEnv

> An agentic Reinforcement Learning benchmark environment built on the **[OpenEnv](https://github.com/openenv/openenv) framework** — evaluates LLM agents on enterprise email triage: classify, summarize, route, and reply.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Server-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

---

## 📌 Overview

**Email Triage OpenEnv** is a structured agentic benchmark where an LLM agent acts as an autonomous email triage system. Built on the **OpenEnv framework**, it exposes a clean REST API (`/reset`, `/step`, `/state`) that any agent can interact with.

The agent receives an email and must produce a structured `MyAction` response:

| Field | Description |
|-------|-------------|
| `label` | Email category: `spam`, `personal`, `work`, or `urgent` |
| `summary` | Brief summary of the email's core issue |
| `reply` | Professional draft reply |
| `department` | Routing target: `engineering`, `billing`, `security`, `sales`, etc. |

---

## 🗂️ Benchmark Tasks

Three tasks are defined in `openenv.yaml` and run sequentially via `inference.py`:

| Task ID | What the Agent Must Do |
|---------|------------------------|
| `email-classification` | Classify the email label (spam / personal / work / urgent) |
| `urgency-detection` | Detect urgency, classify label, draft a contextual reply |
| `spam-filtering` | Identify and filter spam with correct label and routing |

Each task runs up to **3 steps per episode**, cycling through the environment's internal difficulty pool (`easy → medium → hard`) which progressively requires more fields — from label-only classification to full department routing + reply drafting.

---

## 🏗️ How It Works

```
Agent calls POST /reset
        │
        ▼
MyEnvironment loads next task email + instruction
        │
        ▼
Agent receives MyObservation { email, metadata: { task_id, instruction } }
        │
        ▼
Agent calls POST /step with MyAction { label, summary, reply, department }
        │
        ▼
grader.grade() scores the action (label match + summary quality + reply keyword coverage + department routing)
        │
        ▼
Returns { reward: 0.0–1.0, done: bool, observation: next email }
        │
   (repeats up to 3 steps, then done=True)
```

The inference pipeline (`inference.py`) uses a **Dual-Stage Refinement** approach:
1. **Draft Pass** — Qwen2.5-72B generates an initial JSON action via Chain-of-Thought prompting
2. **Reviewer Pass** — A second LLM call critiques and corrects the draft for accuracy and tone before committing the action

---

## 🎯 Reward Function (`grader.py`)

Scores are in the range `[0.01, 0.99]`:

| Component | Condition | Reward |
|-----------|-----------|--------|
| Label (correct) | `action.label == ground_truth.label` | `+0.50` |
| Label (valid but wrong) | Label is one of the 4 valid classes | `+0.10` |
| Summary quality | `len(summary) > 10` | `+0.20` |
| Reply keywords | Keyword hit rate × 0.2 | `+0.00–0.20` |
| Reply (no keywords required) | Any non-empty reply | `+0.10` |
| Department (hard tasks only) | `action.department == ground_truth.department` | `+0.10` |

---

## 📁 Project Structure

```
email-triage-env/
├── my_env_environment.py   # Core OpenEnv environment — episode logic, task pool, step handling
├── grader.py               # Reward scoring via keyword matching and label accuracy
├── inference.py            # Dual-stage LLM agent (Qwen2.5-72B draft + reviewer refinement)
├── models.py               # Pydantic schemas: MyAction, MyObservation
├── server.py               # FastAPI server exposing /reset, /step, /state endpoints
├── client.py               # Test client for local interaction
├── openenv.yaml            # OpenEnv spec: tasks, action space, observation space, reward
├── Dockerfile              # Container for HuggingFace Spaces deployment (port 7860)
└── requirements.txt        # Dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- `openenv-core` library

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

pip install -r requirements.txt
pip install openenv-core

python server.py
# Server starts at http://localhost:7860
```

---

## 🤖 Interacting with the Environment

```python
import requests

BASE = "http://localhost:7860"

# Start a new episode
obs = requests.post(f"{BASE}/reset").json()
print(obs["observation"]["email"])
print(obs["observation"]["metadata"])  # task_id + instruction

# Submit an action
action = {
    "label": "urgent",
    "summary": "Production server is down.",
    "reply": "Hi team, we've escalated this to engineering immediately.",
    "department": "engineering"
}
result = requests.post(f"{BASE}/step", json=action).json()
print(result["reward"])   # float between 0.01 and 0.99
print(result["done"])     # True after all steps complete
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Start a new episode, get first observation |
| `POST` | `/step` | Submit `MyAction`, receive reward + next observation |
| `GET`  | `/state` | Get current `episode_id` and `step_count` |

Interactive docs available at `http://localhost:7860/docs` (FastAPI Swagger UI).

---

## ⚙️ Environment Variables (for inference.py)

| Variable | Description |
|----------|-------------|
| `API_KEY` | LLM provider API key (or `HF_TOKEN`) |
| `API_BASE_URL` | OpenAI-compatible base URL for your model provider |
| `MODEL_NAME` | Model to use (default: `Qwen/Qwen2.5-72B-Instruct`) |
| `SPACE_URL` | URL of the running environment server (default: `http://localhost:7860`) |

---

## 🛠️ Tech Stack

- **Python 3.10+** — environment and agent logic
- **OpenEnv** — agentic RL environment framework
- **FastAPI + Uvicorn** — REST server
- **Pydantic** — action/observation schema validation
- **OpenAI SDK** — LLM inference (OpenAI-compatible endpoint)
- **Docker** — containerized deployment on HuggingFace Spaces

---

## 📄 License

[Apache 2.0](LICENSE)

---

## 👤 Author

**Yashas M**  
B.E. Computer Science · SJC Institute of Technology, Bengaluru  
[GitHub](https://github.com/Yashasm18) · [LinkedIn](https://linkedin.com/in/yashas-m-864192320)
