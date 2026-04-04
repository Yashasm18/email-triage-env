from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_score(text1, text2):
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2))


def grade(task_id, state, action, ground_truth):
    reward = 0.0

    email = state["email"]
    correct_label = ground_truth.get("label")

   
    if action.label == correct_label:
        reward += 0.4

    
    if action.summary:
        sim = semantic_score(email, action.summary)
        if sim > 0.5:
            reward += 0.3

   )
    if task_id == "hard" and action.reply:
        sim = semantic_score(email, action.reply)
        if sim > 0.4:
            reward += 0.3

    return min(reward, 1.0)
