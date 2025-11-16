import os
from pydantic import BaseSettings, Field, ValidationError

class Settings(BaseSettings):
    # Obrigatório
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # Opcionais
    youtube_api_key: str = Field(None, env="YOUTUBE_API_KEY")
    tmdb_api_key: str = Field(None, env="TMDB_API_KEY")

    database_url: str = Field(
        "sqlite+aiosqlite:///./media_recommender.db",
        env="DATABASE_URL"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Load + validate
try:
    settings = Settings()
except ValidationError as e:
    missing = [err["loc"][0] for err in e.errors()]

    raise RuntimeError(
        "\n❌ [ERRO DE CONFIGURAÇÃO]\n"
        "Estas variáveis OBRIGATÓRIAS não foram definidas:\n\n"
        + "\n".join([f" - {m}" for m in missing])
        + "\n\nDefina-as no painel do Render antes do deploy.\n"
    )
