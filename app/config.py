import os
# Importação BaseSettings e ConfigDict do pydantic_settings
from pydantic_settings import BaseSettings, SettingsConfigDict 
from pydantic import Field, ValidationError

class Settings(BaseSettings):
    # Configuração de Ambiente Pydantic v2 (substitui a classe Config da v1)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True 
    )

    # Variável OBRIGATÓRIA
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")

    # Variáveis Opcionais (CORRIGIDO: Tipagem alterada para 'str | None' para aceitar o valor None)
    # Se estas Variáveis de Ambiente não estiverem no Render, elas agora aceitam None sem falhar.
    youtube_api_key: str | None = Field(None, validation_alias="YOUTUBE_API_KEY")
    tmdb_api_key: str | None = Field(None, validation_alias="TMDB_API_KEY")

    # URL do Banco de Dados
    database_url: str = Field(
        "sqlite+aiosqlite:///./media_recommender.db",
        validation_alias="DATABASE_URL"
    )

# Load + validate
try:
    settings = Settings()
except ValidationError as e:
    # A lógica de validação customizada está preservada
    missing = [err["loc"][0] for err in e.errors()]

    raise RuntimeError(
        "\n❌ [ERRO DE CONFIGURAÇÃO]\n"
        "Estas variáveis OBRIGATÓRIAS não foram definidas:\n\n"
        + "\n".join([f" - {m}" for m in missing])
        + "\n\nDefina-as no painel do Render antes do deploy.\n"
    )
```eof

Por favor, substitua seu arquivo local, faça o `commit` e o `push` para que o Render possa iniciar o seu serviço.
