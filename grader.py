def keyword_score(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)


def grade(task_id, state, action, ground_truth):
    reward = 0.01  # Base signal

    # 1. Intent Detection (40%)
    if action.label == ground_truth.get("label"):
        reward += 0.4
    elif action.label in ["work", "urgent"] and ground_truth.get("label") in ["work", "urgent"]:
        reward += 0.1  # Partial credit for recognizing high-priority email

    # 2. Routing Intelligence (30%)
    if hasattr(action, 'department') and action.department == ground_truth.get("department"):
        reward += 0.3
    elif hasattr(action, 'department') and action.department != "none" and ground_truth.get("department") != "none":
        reward += 0.1  # Partial credit for knowing it needs human routing

    # 3. Response Quality (30%)
    if action.reply and len(action.reply) > 30:
        prof_terms = ["sincerely", "regards", "assist", "apologize", "immediately"]
        count = sum(1 for term in prof_terms if term in action.reply.lower())
        reward += min(0.3, count * 0.1)

    return float(max(0.01, min(0.99, reward)))
