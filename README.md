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

# 📧 Email Triage RL Environment

## Overview
A real-world OpenEnv environment where an AI agent learns to triage emails intelligently.

## Tasks
- **Easy**: Classify email as spam/personal/work/urgent
- **Medium**: Classify + write summary + draft reply
- **Hard**: Classify + route to correct department + summary + reply

## Action Space
- `label`: spam | personal | work | urgent
- `summary`: brief email summary
- `reply`: professional reply draft
- `department`: engineering | support | sales | billing | marketing | legal | security | management | none

## Reward
- Scores between 0.0 and 1.0
- Partial credit for correct label, good summary, relevant reply
- Semantic similarity used for reply/summary scoring

## Setup
```bash
pip install openenv-core
openenv fork souller/email-triage-env --repo-id your-username/email-triage-env
```
