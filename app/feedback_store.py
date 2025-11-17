from typing import List
from sqlalchemy.orm import Session
from . import models # Importa o modelo Feedback do DB
from app.feedback import Feedback # Sua classe Pydantic Feedback original

# Removemos o armazenamento em memória (_feedback_storage)

# --------------------------------------
# 💾 Funções de feedback (Agora usam DB)
# --------------------------------------

def save_feedback(db: Session, fb: Feedback):
    """
    Salva um feedback do usuário no banco de dados PostgreSQL.
    Requer a sessão do DB (db: Session) injetada do FastAPI.
    """
    # Cria uma nova instância do modelo do banco de dados (models.Feedback)
    db_feedback = models.Feedback(
        user_id=fb.user_id,
        item_id=fb.item_id,
        liked=fb.liked,
        # O Pydantic se encarrega de garantir que o embedding seja um objeto/lista Python
        embedding=fb.embedding
    )
    db.add(db_feedback)
    db.commit() # Salva no Supabase
    db.refresh(db_feedback)
    return db_feedback

def load_feedback_for_user(db: Session, user_id: str) -> List[models.Feedback]:
    """Carrega todos os feedbacks de um usuário do banco de dados."""
    return db.query(models.Feedback).filter(models.Feedback.user_id == user_id).all()

def get_all_feedback(db: Session) -> List[models.Feedback]:
    """Retorna todos os feedbacks cadastrados do banco de dados."""
    # Retorna os objetos de modelo (que incluem o ID do banco, etc.)
    return db.query(models.Feedback).all()

# NOTA: clear_feedback() foi removido, pois limpar o DB requer cuidados
# especiais (como DELETE FROM) e não deve ser feito em produção.
