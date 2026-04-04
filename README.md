---
title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# Email Triage OpenEnv

A real-world OpenEnv environment where an AI agent triages emails by classifying, summarizing, routing, and replying to them — with increasing difficulty across 3 task levels.

## Action Space
- `label`: spam, personal, work, urgent
- `summary`: brief email summary (medium/hard)
- `reply`: professional reply draft (medium/hard)
- `department`: engineering, support, sales, billing, marketing, legal, security, management, none (hard)

## Tasks
- **Easy**: classify label only
- **Medium**: label + summary + reply
- **Hard**: label + department + summary + reply

## Endpoints
- `POST /reset` — start episode
- `POST /step` — submit action
- `GET /state` — current state

## Run Inference
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your_token"
python inference.py
```
