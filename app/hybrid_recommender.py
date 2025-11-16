from app.recommender import base_recommendations
from app.embeddings import cosine_similarity
from app.feedback_store import load_feedback
def popularity_score(item):
    return float(item.metadata.get("popularity", 0) or 0)
async def hybrid_recommend(prefs, user_id: str = "anon", limit: int = 10):
    pool = await base_recommendations(prefs)
    fb = load_feedback(user_id)
    liked_ids = {f["item_id"] for f in fb if f.get("liked")}
    liked_embeddings = [f.get("embedding") for f in fb if f.get("liked") and f.get("embedding")]
    for r in pool:
        score = r.score
        if prefs.platforms and r.item.platform not in prefs.platforms:
            score -= 0.5
        if prefs.max_duration_minutes and r.item.duration_minutes:
            if r.item.duration_minutes > prefs.max_duration_minutes:
                score -= 0.3
        score += 0.1 * popularity_score(r.item)
        if liked_embeddings and getattr(r.item, "embedding", None):
            sims = [cosine_similarity(r.item.embedding, le) for le in liked_embeddings]
            score += max(sims) * 1.5
        if r.item.id in liked_ids:
            score += 2.0
        r.score = score
    pool.sort(key=lambda x: x.score, reverse=True)
    return pool[:limit]
