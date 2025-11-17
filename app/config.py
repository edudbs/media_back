import os
from pydantic import Field, ValidationError
# CORRIGIDO: BaseSettings e SettingsConfigDict agora vêm de pydantic_settings
from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    # Configuração de Ambiente Pydantic v2 (substitui a classe Config)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True # Mantém a sensibilidade a caixa, como você tinha definido
    )

    # Variáveis OBRIGATÓRIAS
    # Usando validation_alias para mapear o nome da variável Python para a Variável de Ambiente (VE)
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")

    # Variáveis Opcionais (aproveitando as que você tinha)
    youtube_api_key: str = Field(None, validation_alias="YOUTUBE_API_KEY")
    tmdb_api_key: str = Field(None, validation_alias="TMDB_API_KEY")

    # URL do Banco de Dados. O padrão é SQLite, mas a VE DATABASE_URL no Render 
    # deve ser usada para o Supabase.
    database_url: str = Field(
        "sqlite+aiosqlite:///./media_recommender.db",
        validation_alias="DATABASE_URL"
    )

# Load + validate
try:
    settings = Settings()
except ValidationError as e:
    # A lógica de validação da sua versão antiga é compatível com Pydantic v2
    missing = [err["loc"][0] for err in e.errors()]

    raise RuntimeError(
        "\n❌ [ERRO DE CONFIGURAÇÃO]\n"
        "Estas variáveis OBRIGATÓRIAS não foram definidas:\n\n"
        + "\n".join([f" - {m}" for m in missing])
        + "\n\nDefina-as no painel do Render antes do deploy.\n"
    )
