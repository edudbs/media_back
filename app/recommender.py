# Ficheiro: app/recommender.py
from typing import List, Dict, Any, Optional
from app.schemas import RecommendRequest, Recommendation, MediaItem # Import Corrigido
import random

# Base de Dados Mock (para a recomendação simples, não depende do DB do Supabase)
# A função é chamada pelo recommend_endpoint se strategy != hybrid (que não é o caso atual)
MOCK_DATA: List[MediaItem] = [
    MediaItem(id=1, title="Indiana Jones e a Relíquia Perdida", description="Aventura arqueológica épica.", platform="Netflix", duration_minutes=120),
    MediaItem(id=2, title="O Senhor dos Anéis: A Sociedade do Anel", description="Fantasia, aventura e jornada heroica.", platform="Prime Video", duration_minutes=178),
    MediaItem(id=3, title="Duna", description="Ficção científica e política planetária.", platform="HBO Max", duration_minutes=155),
    MediaItem(id=4, title="Breaking Bad", description="Série de drama sobre um professor.", platform="Netflix", duration_minutes=50),
    MediaItem(id=5, title="Blade Runner 2049", description="Filme cyberpunk e distópico.", platform="HBO Max", duration_minutes=164),
    MediaItem(id=6, title="Piratas do Caribe: A Maldição do Pérola Negra", description="Aventura de piratas.", platform="Disney+", duration_minutes=143),
    MediaItem(id=7, title="Interestelar", description="Ficção científica sobre viagem no tempo.", platform="Prime Video", duration_minutes=169),
    MediaItem(id=8, title="Peaky Blinders", description="Série de drama sobre gângsteres.", platform="Netflix", duration_minutes=60),
]

# Funções auxiliares de similaridade e relevância...
# ... (Neste projeto estamos focando no híbrido, mas o simples precisa rodar)

async def recommend(preferences: str, limit: int, user_id: str) -> List[Recommendation]:
    """Recomendação simples baseada em conteúdo (Mock)."""
    
    # Simulação de pontuação baseada em texto (content-based)
    recs = []
    
    # Geramos recomendações aleatórias apenas para simular o resultado
    random.shuffle(MOCK_DATA)
    
    for item in MOCK_DATA[:limit]:
        # Pontuação mock alta se a preferência for aventura
        score = random.uniform(0.7, 0.9) if "aventura" in preferences.lower() else random.uniform(0.5, 0.7)
        
        recs.append(Recommendation(
            item=item,
            score=round(score, 2),
            reason=f"Similar a '{preferences}' por género."
        ))
        
    return recs
