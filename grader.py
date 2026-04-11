def keyword_score(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)


def grade(task_id, state, action, ground_truth):
    reward = 0.01  # Base signal
    feedback_parts = []

    # 1. Intent Detection (40%)
    if action.label == ground_truth.get("label"):
        reward += 0.4
        feedback_parts.append(f"✅ Correct label '{action.label}'.")
    elif action.label in ["work", "urgent"] and ground_truth.get("label") in ["work", "urgent"]:
        reward += 0.1
        feedback_parts.append(f"⚠️ Label '{action.label}' is close but not exact. Expected '{ground_truth.get('label')}'.")
    elif action.label in ["spam", "personal", "work", "urgent"]:
        feedback_parts.append(f"❌ Wrong label '{action.label}'. Expected '{ground_truth.get('label')}'.")
    else:
        feedback_parts.append(f"❌ Invalid label '{action.label}'. Must be one of: spam, personal, work, urgent.")

    # 2. Routing Intelligence (30%)
    if hasattr(action, 'department') and action.department == ground_truth.get("department"):
        reward += 0.3
        feedback_parts.append(f"✅ Correct department '{action.department}'.")
    elif hasattr(action, 'department') and action.department and action.department != "none" and ground_truth.get("department") and ground_truth.get("department") != "none":
        reward += 0.1
        feedback_parts.append(f"⚠️ Department '{action.department}' is wrong. Expected '{ground_truth.get('department')}'.")
    elif ground_truth.get("department") and action.department != ground_truth.get("department"):
        feedback_parts.append(f"❌ Missing correct department. Expected '{ground_truth.get('department')}'.")

    # 3. Summary quality
    if action.summary and len(action.summary) > 10:
        feedback_parts.append("✅ Summary provided.")
    elif ground_truth.get("reply_keywords"):
        feedback_parts.append("⚠️ Summary missing or too short.")

    # 4. Response Quality (30%)
    if action.reply and len(action.reply) > 30:
        prof_terms = ["sincerely", "regards", "assist", "apologize", "immediately"]
        count = sum(1 for term in prof_terms if term in action.reply.lower())
        reward += min(0.3, count * 0.1)
        if count >= 2:
            feedback_parts.append(f"✅ Professional reply with {count} quality terms.")
        elif count == 1:
            feedback_parts.append("⚠️ Reply is okay but could be more professional.")
        else:
            feedback_parts.append("⚠️ Reply lacks professional tone.")
    elif ground_truth.get("reply_keywords"):
        feedback_parts.append("❌ No reply provided.")

    reward = float(max(0.01, min(0.99, reward)))
    feedback = " ".join(feedback_parts) if feedback_parts else "No feedback available."
    feedback = f"Score: {reward:.2f}. " + feedback

    return reward, feedback
