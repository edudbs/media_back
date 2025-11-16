from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class Feedback(BaseModel):
    user_id: str
    item_id: str
    liked: bool
    timestamp: datetime = datetime.utcnow()
    embedding: Optional[list] = None
