import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
import json, os
DATABASE_URL = "sqlite:///./data/embeddings_cache.db"
os.makedirs("data", exist_ok=True)
engine = sa.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class EmbeddingEntry(Base):
    __tablename__ = "embeddings"
    id = Column(String, primary_key=True, index=True)
    text = Column(String)
    embedding = Column(String)
Base.metadata.create_all(bind=engine)
def get_embedding(id: str):
    session = SessionLocal()
    row = session.query(EmbeddingEntry).filter_by(id=id).first()
    session.close()
    if not row:
        return None
    return json.loads(row.embedding)
def set_embedding(id: str, text: str, embedding: list):
    session = SessionLocal()
    row = session.query(EmbeddingEntry).filter_by(id=id).first()
    if row:
        row.embedding = json.dumps(embedding)
        row.text = text
    else:
        row = EmbeddingEntry(id=id, text=text, embedding=json.dumps(embedding))
        session.add(row)
    session.commit()
    session.close()
