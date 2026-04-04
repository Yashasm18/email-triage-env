def keyword_score(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)

def grade(task_id, state, action, ground_truth):
    reward = 0.0
    correct_label = ground_truth.get("label")

    if action.label == correct_label:
        reward += 0.5
    elif action.label in ["spam", "personal", "work", "urgent"]:
        reward += 0.1

    if task_id == "easy":
        return min(reward, 1.0)

    if action.summary and len(action.summary) > 10:
        reward += 0.2

    reply_keywords = ground_truth.get("reply_keywords", [])
    if action.reply and reply_keywords:
        reward += 0.2 * keyword_score(action.reply, reply_keywords)

    if task_id == "hard":
        correct_dept = ground_truth.get("department")
        if action.department == correct_dept:
            reward += 0.1

    return min(reward, 1.0)
