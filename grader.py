def keyword_score(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)


def grade(task_id, state, action, ground_truth):
    reward = 0.01
    feedback_parts = []

    # 1. Label check (works for all task types)
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

    # 2. Department check (spam-filtering task)
    if ground_truth.get("department"):
        if hasattr(action, 'department') and action.department == ground_truth.get("department"):
            reward += 0.3
            feedback_parts.append(f"✅ Correct department '{action.department}'.")
        elif hasattr(action, 'department') and action.department and action.department != "none":
            reward += 0.1
            feedback_parts.append(f"⚠️ Department '{action.department}' is wrong. Expected '{ground_truth.get('department')}'.")
        else:
            feedback_parts.append(f"❌ Missing department. Expected '{ground_truth.get('department')}'.")

    # 3. Summary check (urgency-detection and spam-filtering tasks)
    if task_id in ["urgency-detection", "spam-filtering"]:
        if action.summary and len(action.summary) > 10:
            feedback_parts.append("✅ Summary provided.")
        else:
            feedback_parts.append("⚠️ Summary missing or too short.")

    # 4. Reply quality check (urgency-detection and spam-filtering tasks)
    if task_id in ["urgency-detection", "spam-filtering"]:
        if action.reply and len(action.reply) > 30:
            prof_terms = ["sincerely", "regards", "assist", "apologize", "immediately"]
            count = sum(1 for term in prof_terms if term in action.reply.lower())
            reward += min(0.3, count * 0.1)
            if count >= 2:
                feedback_parts.append(f"✅ Professional reply with {count} quality terms.")
            elif count == 1:
                feedback_parts.append("⚠️ Reply okay but could be more professional.")
            else:
                feedback_parts.append("⚠️ Reply lacks professional tone.")
        else:
            feedback_parts.append("❌ No reply or reply too short.")

    reward = float(max(0.01, min(0.99, reward)))
    feedback = " ".join(feedback_parts) if feedback_parts else "No feedback available."
    feedback = f"Score: {reward:.2f}. " + feedback

    return reward, feedback
