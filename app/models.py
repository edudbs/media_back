from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB 
from app.database import Base # Importa a Base que definimos

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    preferences = Column(JSONB) # Armazena o objeto de preferências

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    item_id = Column(String, index=True, nullable=False)
    liked = Column(Boolean, nullable=False)
    embedding = Column(JSONB, nullable=True) # Armazena o vetor de embedding
