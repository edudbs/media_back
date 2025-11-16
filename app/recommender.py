import asyncio
from typing import List
from app.schemas import Preferences, Recommendation, ContentItem
from app.embeddings import embed_text
from app.feedback_store import load_feedback_for_user
from app.content import load_content  # função que você já possui para carregar base de filmes/músicas/etc.


# -----------------------------------------------------
# 🔢 Similaridade coseno (sem numpy)
# -----------------------------------------------------
def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# -----------------------------------------------------
# 📌 Gera embedding das preferências do usuário
# -----------------------------------------------------
async def embed_preferences(prefs: Preferences) -> List[float]:
    text = ""

    if prefs.genres:
        text += "Gêneros: " + ", ".join(prefs.genres) + ". "

    if prefs.keywords:
        text += "Palavras-chave: " + ", ".join(prefs.keywords) + ". "

    if not text.strip():
        text = "recomendações populares"

    return await embed_text(text)


# -----------------------------------------------------
# 🎯 Sistema básico de recomendação
# -----------------------------------------------------
async def recommend(preferences: Preferences, limit: int = 5, user_id: str = "anon") -> List[Recommendation]:

    # 1) Carrega catálogo
    catalog = load_content()

    # 2) Embedding da preferência atual
    user_emb = await embed_preferences(preferences)

    # 3) Carrega feedback para personalização
    fb = load_feedback_for_user(user_id)

    liked_embeddings = [
        f.embedding for f in fb if f.liked and f.embedding is not None
    ]

    # 4) Calcula similaridade de cada item
    scored = []

    for item in catalog:
        if not item.embedding:
            # calcula embedding do item se ainda não existir
            item.embedding = await embed_text(f"{item.title} {item.description or ''}")

        sim_pref = cosine_similarity(user_emb, item.embedding)

        # Se o usuário tem likes anteriores, aumenta pontuação conforme similaridade média
        sim_liked = 0.0
        if liked_embeddings:
            sims = [cosine_similarity(le, item.embedding) for le in liked_embeddings]
            sim_liked = sum(sims) / len(sims)

        final_score = (sim_pref * 0.7) + (sim_liked * 0.3)

        scored.append((final_score, item))

    # 5) Ordena por pontuação
    scored.sort(key=lambda x: x[0], reverse=True)

    # 6) Cria objetos Recommendation
    recs = []
    for score, item in scored[:limit]:
        recs.append(
            Recommendation(
                item=item,
                score=float(score),
                why=f"Recomendado porque combina com seus gostos ({score:.2f})."
            )
        )

    return recs
