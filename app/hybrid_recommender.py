# Ficheiro: app/hybrid_recommender.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas import RecommendRequest, Recommendation, MediaItem # Import Corrigido
from app.models import Media
import random

# --- Lógica do Recomendador Híbrido ---

async def hybrid_recommend(req: RecommendRequest, user_id: str, limit: int, db: Session) -> List[Recommendation]:
    """
    Combina recomendações baseadas em conteúdo (a partir das preferências) 
    e simula uma filtragem colaborativa (usando o histórico mock).
    
    IMPORTANTE: Esta função precisa do objeto 'db' para interagir com o catálogo 'Media'.
    """
    
    # 1. Obter todos os itens do catálogo (Content-Based Data Source)
    # Apenas o campo 'title' é necessário para a simulação de Content-Based
    try:
        all_media: List[Media] = db.query(Media).all()
    except Exception as e:
        # Se a tabela Media estiver vazia ou com erro, usamos um fallback
        print(f"ERRO: Falha ao carregar mídia do DB. Usando mock. {e}")
        from app.recommender import MOCK_DATA
        all_media = MOCK_DATA

    # Mapear para o formato de esquema e selecionar apenas os títulos
    media_items: List[MediaItem] = [MediaItem.from_orm(item) for item in all_media]
    
    
    # 2. Simulação de Content-Based Scoring
    # Baseado na string de preferência do usuário (req.preferences)
    
    scored_items: List[Recommendation] = []
    
    for item in media_items:
        score_content = 0.0
        
        # Simulação: Pontuar alto para palavras-chave (aventura, épico)
        if any(keyword in item.description.lower() for keyword in ["aventura", "épico", "jornada"]):
            score_content = random.uniform(0.6, 0.9)
        elif any(keyword in item.description.lower() for keyword in ["fantasia", "ficção", "drama"]):
            score_content = random.uniform(0.4, 0.7)
        
        # Simulação de Colaborative/Personalização (Colaborative Filtering/CF)
        # Se o usuário for user_test_001, damos um boost extra em certos itens
        score_cf = 0.0
        if user_id == "user_test_001" and item.id in [1, 2, 6]: # Indiana Jones, Senhor dos Anéis, Piratas
            score_cf = 0.2 
        
        # Pontuação Híbrida: Combinação Simples
        final_score = score_content * 0.7 + score_cf * 0.3
        
        if final_score > 0.5:
            scored_items.append(Recommendation(
                item=item,
                score=round(final_score, 2),
                reason="Conteúdo (70%) + Similaridade de Usuários (30%)"
            ))

    # 3. Filtragem e Classificação
    # Ordenar por pontuação e aplicar o limite
    scored_items.sort(key=lambda r: r.score, reverse=True)
    
    return scored_items[:limit]
