from pydantic import BaseModel
from typing import List, Optional
from app.schemas import Preferences, ContentItem

class FeedbackRequest(BaseModel):
    user_id: str
    item_id: str
    liked: bool

class ProfileRequest(BaseModel):
    user_id: str
    name: str
    preferences: dict

class PlaylistRequest(BaseModel):
    user_id: str
    preferences: Preferences
    limit: Optional[int] = 20
    target_minutes: Optional[int] = 90
