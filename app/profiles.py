from sqlalchemy.orm import Session
from . import models # Importa os modelos Profile
from .schemas_extended import ProfileRequest 

# Assume que você tem a classe ProfileRequest definida corretamente

def save_profile(db: Session, user_id: str, name: str, preferences: dict):
    """Cria ou atualiza um perfil no PostgreSQL."""
    db_profile = db.query(models.Profile).filter(
        models.Profile.user_id == user_id, 
        models.Profile.name == name
    ).first()

    if db_profile:
        # Atualiza o perfil existente
        db_profile.preferences = preferences
    else:
        # Cria um novo perfil
        db_profile = models.Profile(
            user_id=user_id, 
            name=name, 
            preferences=preferences
        )
        db.add(db_profile)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def load_profiles(db: Session, user_id: str) -> dict:
    """Carrega todos os perfis de um usuário."""
    profiles_list = db.query(models.Profile).filter(
        models.Profile.user_id == user_id
    ).all()
    
    # Converte a lista de modelos do DB para um dicionário (como o JSON antigo fazia)
    profiles_dict = {
        profile.name: {
            "name": profile.name,
            "preferences": profile.preferences
        } for profile in profiles_list
    }
    return profiles_dict

def get_profile_by_name(db: Session, user_id: str, name: str):
    """Busca um perfil específico."""
    return db.query(models.Profile).filter(
        models.Profile.user_id == user_id,
        models.Profile.name == name
    ).first()
