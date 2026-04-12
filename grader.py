def keyword_score(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)


def has_negation(text, label):
    """Penalize responses that explicitly negate the correct label."""
    if not text:
        return False
    text_lower = text.lower()
    negation_patterns = [
        f"not {label}", f"isn't {label}", f"is not {label}",
        f"no {label}", f"not a {label}", f"not an {label}"
    ]
    return any(pattern in text_lower for pattern in negation_patterns)


def grade(task_id, state, action, ground_truth):
    reward = 0.01
    feedback_parts = []

    correct_label = ground_truth.get("label")

    # ── Negation penalty ──────────────────────────────────────────
    reply_text = (action.reply or "") + " " + (action.summary or "")
    if has_negation(reply_text, correct_label):
        feedback_parts.append(f"❌ Negation detected — response incorrectly dismisses '{correct_label}'.")
        reward = float(max(0.01, min(0.99, reward)))
        feedback = "Score: 0.01. " + " ".join(feedback_parts)
        return 0.01, feedback

    # ── 1. Label check ────────────────────────────────────────────
    if action.label == correct_label:
        reward += 0.40
        feedback_parts.append(f"✅ Correct label '{action.label}'.")
    elif action.label in ["work", "urgent"] and correct_label in ["work", "urgent"]:
        reward += 0.10
        feedback_parts.append(f"⚠️ Label '{action.label}' is close. Expected '{correct_label}'.")
    elif action.label in ["spam", "personal", "work", "urgent"]:
        feedback_parts.append(f"❌ Wrong label '{action.label}'. Expected '{correct_label}'.")
    else:
        feedback_parts.append(f"❌ Invalid label '{action.label}'. Must be: spam, personal, work, urgent.")

    # ── 2. Department check ───────────────────────────────────────
    if ground_truth.get("department"):
        if hasattr(action, "department") and action.department == ground_truth.get("department"):
            reward += 0.25
            feedback_parts.append(f"✅ Correct department '{action.department}'.")
        elif hasattr(action, "department") and action.department and action.department != "none":
            reward += 0.08
            feedback_parts.append(f"⚠️ Department '{action.department}' wrong. Expected '{ground_truth.get('department')}'.")
        else:
            feedback_parts.append(f"❌ Missing department. Expected '{ground_truth.get('department')}'.")

    # ── 3. Summary check ──────────────────────────────────────────
    if task_id in ["urgency-detection", "spam-filtering"]:
        if action.summary and len(action.summary) > 15:
            reward += 0.15
            feedback_parts.append("✅ Good summary provided.")
        elif action.summary and len(action.summary) > 5:
            reward += 0.05
            feedback_parts.append("⚠️ Summary too short.")
        else:
            feedback_parts.append("❌ No summary provided.")

    # ── 4. Reply quality ──────────────────────────────────────────
    if task_id in ["urgency-detection", "spam-filtering"]:
        if action.reply and len(action.reply) > 30:
            prof_terms = ["sincerely", "regards", "assist", "apologize",
                          "immediately", "investigate", "escalate", "resolve"]
            count = sum(1 for term in prof_terms if term in action.reply.lower())
            reply_bonus = min(0.20, count * 0.05)
            reward += reply_bonus
            if count >= 3:
                feedback_parts.append(f"✅ Professional reply with {count} quality terms.")
            elif count >= 1:
                feedback_parts.append(f"⚠️ Reply okay but could be more professional ({count} terms).")
            else:
                feedback_parts.append("⚠️ Reply lacks professional tone.")
        else:
            feedback_parts.append("❌ No reply or reply too short.")

    reward = float(max(0.01, min(0.99, reward)))
    feedback = f"Score: {reward:.2f}. " + " ".join(feedback_parts)
    return reward, feedback
