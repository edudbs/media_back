import asyncio, numpy as np
from typing import List
from openai import OpenAI
from app.tools.youtube import search_youtube
from app.tools.tmdb import search_tmdb
from app.schemas import ContentItem, Preferences, Recommendation
from app.config import settings
from app.embeddings import embed_text, cosine_similarity
from app.embeddings_cache import get_embedding, set_embedding
client = OpenAI(api_key=settings.openai_api_key)
async def base_recommendations(preferences: Preferences, limit_each: int = 5) -> List[Recommendation]:
    qbase = " ".join(preferences.genres or [])
    qmood = " ".join(preferences.mood or [])
    base = (qbase + " " + qmood).strip() or "recommended"
    yt_items = await search_youtube(base + " short film", max_results=limit_each)
    tmdb_items = await search_tmdb(base, max_results=limit_each, media_type="movie")
    items = []
    for i in yt_items + tmdb_items:
        item = ContentItem(**i)
        # get embedding from cache or create
        emb = get_embedding(item.id)
        if emb is None:
            emb = await embed_text(f"{item.title} {item.description or ''}")
            set_embedding(item.id, f"{item.title} {item.description or ''}", emb)
        item.embedding = emb
        items.append(item)
    # simple initial scoring: cosine with pref embedding
    pref_text = " ".join([" ".join(preferences.genres or []), " ".join(preferences.mood or [])]).strip() or "general entertainment"
    pref_emb = get_embedding('pref:' + pref_text) or await embed_text(pref_text)
    set_embedding('pref:' + pref_text, pref_text, pref_emb)
    scored = []
    for item in items:
        score = cosine_similarity(pref_emb, item.embedding)
        scored.append(Recommendation(item=item, score=score, why=f"Similaridade {score:.2f}"))
    return scored
async def recommend(preferences: Preferences, limit: int = 10, user_id: str = "anon") -> List[Recommendation]:
    base = await base_recommendations(preferences, limit_each=6)
    # by default return top-N by embeddings
    base.sort(key=lambda x: x.score, reverse=True)
    return base[:limit]
