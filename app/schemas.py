# Ficheiro: app/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Modelos de Dados ---

class MediaItem(BaseModel):
    """Representa um item de conteúdo multimédia no nosso catálogo."""
    id: int
    title: str
    description: str
    platform: str
    duration_minutes: Optional[int]

class Recommendation(BaseModel):
    """Representa uma recomendação com uma pontuação de relevância."""
    item: MediaItem
    score: float
    reason: Optional[str] = None

# --- Modelo de Pedido (Input) ---

class RecommendRequest(BaseModel):
    """Modelo de pedido para a função de recomendação."""
    preferences: str = Field(..., description="Descrição das preferências do utilizador (ex: 'Filmes de aventura, como Indiana Jones.').")
    platforms: Optional[List[str]] = Field(None, description="Lista opcional de plataformas a considerar.")
    max_duration_minutes: Optional[int] = Field(None, description="Duração máxima em minutos.")
    # Corrigido: O campo 'limit' tem um valor padrão para ser opcional
    limit: int = Field(5, gt=0, description="Número máximo de recomendações a retornar.")

# --- Modelo de Feedback ---

class FeedbackRequest(BaseModel):
    user_id: str
    item_id: int
    feedback_type: str = Field(..., description="Tipo de feedback (ex: 'like', 'dislike', 'viewed').")

# --- Modelo de Perfil ---

class UserProfile(BaseModel):
    user_id: str
    history: List[str] = Field(default_factory=list)
    preferences: str = ""

# --- Modelo de Playlist ---

class PlaylistRequest(BaseModel):
    user_id: str
    item_id: int
    action: str = Field(..., description="Ação na playlist (ex: 'add', 'remove').")

 
