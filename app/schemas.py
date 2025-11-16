from pydantic import BaseModel
from typing import List, Optional
class Preferences(BaseModel):
    genres: Optional[List[str]] = []
    mood: Optional[List[str]] = []
    max_duration_minutes: Optional[int] = None
    platforms: Optional[List[str]] = []
    language: Optional[str] = "pt"
class ContentItem(BaseModel):
    id: str
    title: str
    description: Optional[str]
    platform: str
    url: Optional[str]
    duration_minutes: Optional[int]
    metadata: Optional[dict]
    embedding: Optional[list] = None
class Recommendation(BaseModel):
    item: ContentItem
    score: float
    why: str
class RecommendRequest(BaseModel):
    preferences: Preferences
    limit: Optional[int] = 10
