def grade(task_id, state, action, ground_truth):
    reward = 0.05 
    if action.label == ground_truth.get("label"): reward += 0.50
    elif action.label in ["spam", "personal", "work", "urgent"]: reward += 0.10
    if action.summary and len(action.summary) > 10: reward += 0.20
    if action.reply and len(action.reply) > 5:
        reward += 0.10 
        if any(k.lower() in action.reply.lower() for k in ground_truth.get("reply_keywords", [])):
            reward += 0.09 
    if task_id == "spam-filtering" and hasattr(action, 'department'):
        if action.department == ground_truth.get("department"): reward += 0.05
    return float(max(0.01, min(0.99, reward)))
