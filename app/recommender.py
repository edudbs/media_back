# app/recommender.py

import asyncio
from typing import List, Dict
import numpy as np

from app.schemas import Preferences, Recommendation, ContentItem
from app.feedback_store import load_feedback_for_user
from app.embeddings import embed_text
from app.sessions import get_session

# -----------------------------------------------------
# 🎯 Função principal de recomendação
# -----------------------------------------------------
async def recommend(preferences: Preferences, limit: int = 5, user_id: str = "anon") -> List[Recommendation]:
    """
    Retorna recomendações para o usuário com base em:
      - Preferências fornecidas
      - Feedback passado
      - Embeddings (similaridade semântica)
      - Histórico de sessões
    """
    # 1️⃣ Carrega feedback passado do usuário
    feedbacks = load_feedback_for_user(user_id)

    liked_embeddings = [f.embedding for f in feedbacks if f.liked and f.embedding is not None]

    # 2️⃣ Busca itens candidatos (simulado; em produção, viria do YouTube, TMDB etc.)
    candidates = await _get_candidate_items(preferences, limit * 5)

    # 3️⃣ Score híbrido: similaridade + popularidade + regras simples
    scored = []
    for item in candidates:
        score = 0.0

        # 🎯 Similaridade com embeddings de itens curtidos
        if liked_embeddings:
            item_emb = await embed_text(f"{item.title} {item.description or ''}")
            sims = [np.dot(item_emb, e) / (np.linalg.norm(item_emb) * np.linalg.norm(e)) for e in liked_embeddings]
            score += max(sims)  # pega a maior similaridade

        # 📈 Popularidade simulada
        score += item.popularity or 0

        # ✅ Regras simples (ex: gênero preferido)
        if item.genre and any(g.lower() in [p.lower() for p in preferences.genres] for g in item.genre):
            score += 0.5

        scored.append((item, score))

    # 4️⃣ Ordena por score
    scored.sort(key=lambda x: x[1], reverse=True)

    # 5️⃣ Gera objeto de resposta
    recommendations = []
    for item, score in scored[:limit]:
        why = f"Recomendado por similaridade e preferência" if score > 0 else "Sugestão aleatória"
        recommendations.append(Recommendation(item=item, why=why))

    # 6️⃣ Salva na sessão (últimas recomendações)
    get_session(user_id)["last_recs"] = [r.item.dict() for r in recommendations]

    return recommendations

# -----------------------------------------------------
# 🔹 Função simulada de obtenção de itens
# -----------------------------------------------------
async def _get_candidate_items(preferences: Preferences, max_items: int = 20) -> List[ContentItem]:
    """
    Retorna itens simulados. Substituir por integração real com YouTube, TMDB, Netflix, etc.
    """
    items = []
    for i in range(max_items):
        items.append(ContentItem(
            id=f"item{i}",
            title=f"{preferences.genres[0].title()} Show {i}",
            description=f"Descrição de {preferences.genres[0].title()} {i}",
            url=None,
            genre=[preferences.genres[0]],
            popularity=np.random.rand()
        ))
    await asyncio.sleep(0)  # simula async
    return items
