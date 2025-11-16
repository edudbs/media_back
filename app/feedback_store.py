# app/feedback_store.py

from typing import List, Dict
from app.feedback import Feedback

# --------------------------------------
# 📦 Armazenamento simples em memória
# --------------------------------------
# Em produção, você pode trocar por SQLite, PostgreSQL, etc.
_feedback_storage: List[Feedback] = []

# --------------------------------------
# 💾 Funções de feedback
# --------------------------------------
def save_feedback(feedback: Feedback):
    """Salva um feedback do usuário."""
    _feedback_storage.append(feedback)

def load_feedback_for_user(user_id: str) -> List[Feedback]:
    """Carrega todos os feedbacks de um usuário."""
    return [f for f in _feedback_storage if f.user_id == user_id]

def get_all_feedback() -> List[Feedback]:
    """Retorna todos os feedbacks cadastrados."""
    return _feedback_storage.copy()

def clear_feedback():
    """Limpa todos os feedbacks (útil para testes)."""
    _feedback_storage.clear()
