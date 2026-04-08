def grade(task_id, state, action, ground_truth):
    reward = 0.0
    correct_label = ground_truth.get("label")

    # 1. ACCURACY (Weight: 50%)
    if action.label == correct_label:
        reward += 0.5
    elif action.label in ["spam", "personal", "work", "urgent"]:
        reward += 0.1 

    # 2. ANALYSIS QUALITY (Weight: 30%)
    if action.summary and len(action.summary) > 25:
        reward += 0.15
    
    prof_words = ["sincerely", "assist", "reach out", "support", "regards", "apologize", "immediately"]
    if action.reply and any(word in action.reply.lower() for word in prof_words):
        reward += 0.15

    # 3. ENTERPRISE ROUTING (Weight: 20% - Hard Tasks)
    if task_id == "spam-filtering":
        if hasattr(action, 'department') and action.department == ground_truth.get("department"):
            reward += 0.2
    
    # Range Clip for Hackathon Validation
    return float(max(0.01, min(0.99, reward)))
