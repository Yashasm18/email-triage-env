def grade(task_id, state, action, ground_truth):
    """
    Score an agent action against ground truth.

    Reward breakdown (sums to 1.0 max before clamping):
      - Label correctness  : 0.50 (exact) or 0.10 (partial — both work/urgent)
      - Summary quality    : 0.20 (len > 10 chars)
      - Reply keywords     : 0.00–0.20 (hit-rate × 0.20); if no keywords required, 0.10 for any reply
      - Department routing : 0.10 (hard tasks only, exact match)

    Returns a float in [0.01, 0.99].
    """
    reward = 0.01  # base signal — never zero

    # ── 1. Label correctness (50%) ──────────────────────────────────────────
    if action.label == ground_truth.get("label"):
        reward += 0.50
    elif (
        action.label in ["work", "urgent"]
        and ground_truth.get("label") in ["work", "urgent"]
    ):
        reward += 0.10  # partial: recognised high-priority intent

    # ── 2. Summary quality (20%) ─────────────────────────────────────────────
    if action.summary and len(action.summary.strip()) > 10:
        reward += 0.20

    # ── 3. Reply keyword coverage (20%) ─────────────────────────────────────
    keywords = ground_truth.get("reply_keywords", [])
    if keywords:
        if action.reply:
            reply_lower = action.reply.lower()
            hit_rate = sum(1 for kw in keywords if kw in reply_lower) / len(keywords)
            reward += round(hit_rate * 0.20, 4)
    else:
        # No keywords required — partial credit for any non-empty reply
        if action.reply and len(action.reply.strip()) > 10:
            reward += 0.10

    # ── 4. Department routing (10%, hard tasks only) ─────────────────────────
    if task_id == "spam-filtering":  # hard difficulty
        if (
            action.department
            and action.department == ground_truth.get("department")
        ):
            reward += 0.10

    return float(max(0.01, min(0.99, reward)))
