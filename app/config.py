import os
from pydantic import BaseSettings, Field, ValidationError

class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    youtube_api_key: str = Field(..., env="YOUTUBE_API_KEY")
    tmdb_api_key: str = Field(..., env="TMDB_API_KEY")
    database_url: str = Field("sqlite+aiosqlite:///./media_recommender.db", env="DATABASE_URL")
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_whatsapp_number: str = Field(..., env="TWILIO_WHATSAPP_NUMBER")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Load + validate
try:
    settings = Settings()
except ValidationError as e:
    missing = []
    for err in e.errors():
        missing.append(err["loc"][0])

    raise RuntimeError(
        "\n[ERRO DE CONFIGURAÇÃO]\n"
        "As seguintes variáveis de ambiente obrigatórias não foram definidas:\n\n"
        + "\n".join([f" - {m}" for m in missing])
        + "\n\nDefina todas no painel do Render antes do deploy."
    )
