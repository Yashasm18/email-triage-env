def grade(task_id, state, action, ground_truth):
    reward = 0.01 # Base
    
    # 1. Label Check
    if action.label == ground_truth.get("label"):
        reward += 0.50
    elif action.label in ["spam", "personal", "work", "urgent"]:
        reward += 0.10
        
    # 2. Summary Quality
    if action.summary and len(action.summary) > 10:
        reward += 0.20
        
    # 3. Reply Logic
    if action.reply and len(action.reply) > 0:
        reward += 0.10 # Base for non-empty reply
        keywords = ground_truth.get("reply_keywords", [])
        if keywords:
            hits = sum(1 for k in keywords if k.lower() in action.reply.lower())
            reward += (hits / len(keywords)) * 0.20 # Keyword hit rate
            
    # 4. Department (Hard tasks)
    if task_id == "spam-filtering":
        if action.department == ground_truth.get("department"):
            reward += 0.10
            
    return float(max(0.01, min(0.99, reward)))
