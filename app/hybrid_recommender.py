import numpy as np
import asyncio
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from math import sqrt

from fastapi import Depends
from sqlalchemy.orm import Session 

from app.schemas import Item, Recommendation, RecommendRequest 
from app.config import settings
from app.data import load_all_items
from app.embeddings import embed_text, calculate_cosine_similarity
from app.feedback_store import load_embeddings_for_user 
from app.database import get_db

# Para evitar erros de importação circular de dependência do DB em tempo de execução
if TYPE_CHECKING:
    from app.feedback_store import load_feedback_for_user 

# Cache de itens e embeddings (em memória)
all_items: List[Item] = []
item_embeddings: Dict[str, List[float]] = {}

def load_data_if_needed():
    """Carrega dados e embeddings de forma síncrona se ainda não estiverem carregados."""
    global all_items, item_embeddings
    if not all_items:
        print("⏳ Carregando itens e embeddings...")
        data = load_all_items()
        all_items = data['items']
        item_embeddings = data['embeddings']
        print(f"✅ Dados carregados. Total de itens: {len(all_items)}")

# -----------------------------------------------------
# Lógica de Busca de Recomendação (Função de utilidade)
# -----------------------------------------------------

# Função auxiliar para popularidade (do seu código antigo)
def popularity_score(item: Item) -> float:
    """Retorna a pontuação de popularidade de um item (normalizada ou não)."""
    # Assumimos que 'popularity' está em item.metadata. Se não existir, retorna 0.
    return float(item.metadata.get("popularity", 0) or 0)

async def get_recommendations(
    req: RecommendRequest, # Agora recebe a requisição completa
    user_embeddings: Optional[List[List[float]]] = None,
    liked_item_ids: Optional[set] = None # NOVO: IDs dos itens que o usuário já curtiu
) -> List[Recommendation]:
    """
    Gera embeddings e busca itens semelhantes, aplicando regras de negócio e personalização.
    """
    
    query_text = req.preferences
    limit = req.limit
    
    # 1. Obter embedding para a consulta
    query_embedding = await embed_text(query_text)

    # 2. Personalização: Combinar histórico com a consulta atual
    search_vector = query_embedding
    if user_embeddings and len(user_embeddings) > 0:
        print(f"✨ Personalizando a busca com {len(user_embeddings)} embeddings históricos...")
        
        user_profile_vector = np.mean(np.array(user_embeddings), axis=0).tolist()
        
        # Média Ponderada: 60% da consulta atual, 40% do perfil histórico
        search_vector = [
            (0.6 * query_embedding[i]) + (0.4 * user_profile_vector[i])
            for i in range(len(query_embedding))
        ]

    # 3. Calcular similaridade e aplicar ajustes
    similarities = []
    id_to_item = {item.id: item for item in all_items}
    
    for item_id, item_emb in item_embeddings.items():
        item = id_to_item.get(item_id)
        if not item or not item_emb:
            continue
            
        # 3.1. Calcular a pontuação base (Similaridade Cosseno)
        base_score = calculate_cosine_similarity(search_vector, item_emb)
        final_score = base_score
        
        # 3.2. Aplicar Regras de Negócio (Baseado no seu código antigo)
        
        # Ajuste de Plataforma
        if req.platforms and item.platform not in req.platforms:
            final_score *= 0.8 # Reduz 20% da pontuação se a plataforma não for a desejada
            
        # Ajuste de Duração (Penalidade se for muito longo)
        if req.max_duration_minutes and item.duration_minutes:
            if item.duration_minutes > req.max_duration_minutes:
                 final_score *= 0.9 # Reduz 10% da pontuação
                 
        # Bônus de Popularidade (Adiciona um pequeno impulso)
        # Assumindo que popularity_score retorna um valor entre 0 e 100
        final_score += 0.001 * popularity_score(item) 
        
        # 3.3. REGRAS DE EXCLUSÃO (Muito importante para produção)
        # Removemos itens que o usuário já curtiu
        if liked_item_ids and item.id in liked_item_ids:
            continue # Pula este item; não queremos recomendar algo que ele já gostou.
        
        similarities.append((final_score, item_id))
    
    # 4. Classificar e Selecionar os Top K
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    top_k = similarities[:limit]
    
    # 5. Mapear e formatar a saída
    recommendations = []
    for score, item_id in top_k:
        item = id_to_item.get(item_id)
        if item:
            recommendations.append(Recommendation(
                item=item,
                score=score
            ))

    return recommendations

# -----------------------------------------------------
# Função principal chamada pelo endpoint /recommend
# -----------------------------------------------------

async def hybrid_recommend(
    req: RecommendRequest, # Recebe a requisição completa
    user_id: str, 
    limit: int = 10,
    db: Session = Depends(get_db) 
) -> List[Recommendation]:
    """
    Recomendações híbridas que combinam a consulta (Content-Based) 
    com o histórico de feedback do usuário (Collaborative Filtering via embeddings)
    e regras de negócio.
    """
    
    # Garantir que os dados estejam carregados
    load_data_if_needed()
    
    # 1. Carregar embeddings e IDs dos itens que o usuário curtiu
    user_embeddings = load_embeddings_for_user(db, user_id)
    
    # Para exclusão de itens que já foram curtidos
    from app.feedback_store import load_feedback_for_user 
    liked_feedback = load_feedback_for_user(db, user_id)
    liked_ids = {fb.item_id for fb in liked_feedback if fb.liked}
    
    # 2. Obter recomendações, passando o histórico e as regras
    recommendations = await get_recommendations(
        req=req,
        user_embeddings=user_embeddings,
        liked_item_ids=liked_ids
    )
    
    return recommendations
