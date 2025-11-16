from pydantic import BaseModel
from typing import List, Optional
from app.schemas import Preferences, ContentItem

# -------------------------------
# Feedback
# -------------------------------
class FeedbackRequest(BaseModel):
    user_id: str
    item_id: str
    liked: bool

# -------------------------------
# Perfil de usuário
# -------------------------------
class ProfileRequest(BaseModel):
    user_id: str
    name: str
    preferences: dict  # pode ser { "genres": [...], "mood": [...], ... }

# -------------------------------
# Playlist
# -------------------------------
class PlaylistRequest(BaseModel):
    user_id: str
    preferences: Preferences
    limit: Optional[int] = 20
    target_minutes: Optional[int] = 90
