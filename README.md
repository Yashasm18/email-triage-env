# 📧 Email Triage OpenEnv

> A Reinforcement Learning benchmark environment for evaluating LLM agents on real-world enterprise email triage — built on the [OpenEnv](https://github.com/openenv/openenv) framework.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

---

## 📌 Overview

**Email Triage OpenEnv** is a structured agentic benchmark that tests whether an LLM can act as an autonomous email triage agent. The agent must:

- **Classify** incoming emails (spam / personal / work / urgent)
- **Summarize** the core issue
- **Route** to the correct department (engineering, billing, security, etc.)
- **Draft** a professional reply

Tasks scale across 3 difficulty levels — `easy`, `medium`, and `hard` — with a keyword-based reward function that grades the quality of each action.

---

## 🗂️ Task Levels

| Level | Agent Must | Graded On |
|--------|-----------|-----------|
| **Easy** | Classify the email | `label` accuracy |
| **Medium** | Classify + summarize + reply | `label` + reply keyword matching |
| **Hard** | Classify + route + summarize + reply | `label` + `department` + reply keywords |

### Example Tasks

**Easy:**
> `"URGENT: Production server is down, fix immediately!"`  
> Expected label: `urgent` → department: `engineering`

**Hard:**
> `"Server memory usage has been climbing steadily for 3 days — now at 94%. Logs show unusual traffic patterns from 3 IPs."`  
> Expected: `label: urgent`, `department: security`, reply must include keywords like `investigate`, `block`, `escalate`

---

## 🏗️ Architecture

```
Incoming Email
      │
      ▼
 MyEnvironment.reset()         ← starts a new episode, loads first task
      │
      ▼
 MyObservation                 ← email text + instruction + task_id
      │
      ▼
 LLM Agent (your model)        ← produces MyAction (label, department, summary, reply)
      │
      ▼
 MyEnvironment.step(action)
      │
      ▼
 grader.grade()                ← keyword-based reward scoring
      │
      ▼
 reward + next observation     ← loops through easy → medium → hard
```

The environment runs **3 steps per episode** (one per difficulty level). Each step loads a random email from the current difficulty pool.

---

## 🎯 Reward Function

Scoring is handled in `grader.py` using keyword-based heuristics:

| Task | Reward Components |
|------|------------------|
| Easy | `+1.0` correct label |
| Medium | `+0.5` label, `+0.5` reply keywords hit |
| Hard | `+0.4` label, `+0.3` department, `+0.3` reply keywords hit |

Scores range from `0.0` to `1.0` per step.

---

## 📁 Project Structure

```
email-triage-env/
├── my_env_environment.py   # Core RL environment (tasks, step logic, episode management)
├── grader.py               # Reward calculation engine
├── inference.py            # Agent inference pipeline
├── models.py               # Pydantic models: MyAction, MyObservation
├── server.py               # FastAPI server (OpenEnv-compatible endpoints)
├── client.py               # Test client to interact with the environment
├── openenv.yaml            # OpenEnv spec configuration
├── Dockerfile              # Containerized deployment
└── requirements.txt        # Dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)

### Option 1: Run with Docker

```bash
git clone https://github.com/Yashasm18/email-triage-env.git
cd email-triage-env

docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

### Option 2: Run Locally

```bash
git clone https://github.com/Yashasm18/email-triage-env.git
cd email-triage-env

pip install -r requirements.txt
pip install openenv-core

python server.py
```

The server starts at `http://localhost:7860`.

---

## 🤖 Using the Environment

```python
from my_env_environment import MyEnvironment
from models import MyAction

env = MyEnvironment()
obs = env.reset()

print(obs.email)        # Incoming email text
print(obs.metadata)     # Task ID + instruction

# Agent produces an action
action = MyAction(
    label="urgent",
    department="engineering",
    summary="Production server is down.",
    reply="Hi team, we've escalated this to the engineering team immediately."
)

result = env.step(action)
print(result.reward)    # Reward score for this step
print(result.done)      # True after all 3 difficulty levels complete
```

---

## 🔌 OpenEnv API Endpoints

Once running, the following REST endpoints are available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Start a new episode |
| `POST` | `/step` | Submit an action, get reward + next obs |
| `GET`  | `/tasks` | List available task configurations |

---

## 🛠️ Tech Stack

- **Python 3.10+** — core environment logic
- **FastAPI** — REST server for OpenEnv compatibility
- **Pydantic** — action/observation schema validation
- **Docker** — containerized deployment
- **OpenEnv** — agentic RL environment framework

---

## 📄 License

[Apache 2.0](LICENSE)

---

## 👤 Author

**Yashas M**  
B.E. Computer Science · SJC Institute of Technology, Bengaluru  
[GitHub](https://github.com/Yashasm18) · [LinkedIn](https://linkedin.com/in/yashas-m-864192320)
