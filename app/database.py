from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# A URL é lida do Render (ex: postgresql://...)
DATABASE_URL = settings.database_url

# Cria o "motor" de conexão
# O pool_pre_ping=True ajuda a manter a conexão viva
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Cria uma fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nossos modelos (tabelas)
Base = declarative_base()

# Função de dependência para injetar a sessão da DB nos endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
