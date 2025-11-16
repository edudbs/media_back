import os
from dotenv import load_dotenv
from pydantic import BaseSettings
load_dotenv()
class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY")
    tmdb_api_key: str = os.getenv("TMDB_API_KEY")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./media_recommender.db")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_whatsapp_number: str = os.getenv("TWILIO_WHATSAPP_NUMBER")
settings = Settings()
