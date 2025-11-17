from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session # NOVO: Para injetar a sessão do DB

from app.schemas import RecommendRequest, Recommendation
from app.recommender import recommend
from app.config import settings
from app.feedback import Feedback
from app.feedback_store import save_feedback, get_all_feedback
from app.embeddings import embed_text
from app.sessions import set_session, get_session
from app.profiles import save_profile, load_profiles, get_profile_by_name # As funções agora esperam 'db'
from app.playlist import generate_playlist
from app.schemas_extended import FeedbackRequest, ProfileRequest, PlaylistRequest

# Imports de conexão com o DB
from app.database import engine, Base, get_db # NOVO: Funções de conexão e dependência
from . import models # NOVO: Importa os modelos (tabelas)

from openai import OpenAI
from typing import List

# Validação das variáveis de ambiente
REQUIRED_ENV_VARS = {
    "OPENAI_API_KEY": settings.openai_api_key,
    "DATABASE_URL": settings.database_url
}
missing = [key for key, value in REQUIRED_ENV_VARS.items() if not value]
if missing:
    raise RuntimeError(
        f"❌ Environment variables missing: {', '.join(missing)}"
    )

# Inicialização
client = OpenAI(api_key=settings.openai_api_key)
app = FastAPI(title="Media Recommender API")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
# Cria as tabelas (Profile, Feedback) no Supabase se elas não existirem
try:
    # A base de metadados cria todas as tabelas definidas em app/models.py
    models.Base.metadata.create_all(bind=engine)
    print("✅ Tabelas do banco de dados verificadas/criadas no Supabase.")
except Exception as e:
    print(f"❌ ERRO CRÍTICO ao conectar ou criar tabelas: {e}")
    # É importante lançar o erro para que o Render saiba que o serviço falhou
    raise e 
# ----------------------------------------

# --- CORREÇÃO DE CORS ---
# *** SUBSTITUA ESTA URL PELA SUA URL REAL DO VERCEL! ***
origins = [
    "https://SEU-PROJETO-FRONT.vercel.app",  
    "http://localhost:3000",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # USAR LISTA ESPECÍFICA, NÃO "*"
    allow_credentials=True,      
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# NOVO HANDLER: Permite que a requisição OPTIONS (preflight) passe sem corpo JSON
@app.options("/recommend")
async def options_recommend():
    """Lida com a requisição OPTIONS CORS para /recommend."""
    return {"status": "ok"}

# NOVO ENDPOINT: Leitura de todos os feedbacks (COM DB)
@app.get("/feedbacks")
def get_feedbacks(db: Session = Depends(get_db)):
    """Retorna todos os feedbacks cadastrados no banco de dados."""
    # Chamando a função de persistência que consulta o DB
    return get_all_feedback(db=db)

# Endpoint de recomendação (AGORA COM DB INJETADO E CHAMADA CORRIGIDA)
@app.post("/recommend", response_model=List[Recommendation])
def recommend_endpoint(
    req: RecommendRequest, 
    user_id: str = "anon", 
    strategy: str = "hybrid",
    db: Session = Depends(get_db) # <--- ESSENCIAL: Injeção do DB
):
    try:
        if strategy == "hybrid":
            from app.hybrid_recommender import hybrid_recommend
            # ESSENCIAL: Passar o objeto DB (db=db) na chamada
            recs = await hybrid_recommend(req=req, user_id=user_id, limit=req.limit, db=db) 
        else:
            from app.recommender import recommend
            recs = await recommend(req.preferences, limit=req.limit, user_id=user_id)
        
        set_session(user_id, {"last_recs": [r.item.dict() for r in recs]})
        return recs
    except Exception as e:
        print(f"Erro na recomendação: {e}") 
        raise HTTPException(status_code=500, detail=f"Erro no serviço de recomendação: {str(e)}")

# Endpoint de feedback (CORRIGIDO: Agora injeta DB e chama save_feedback com 'db')
@app.post("/feedback")
async def post_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)): # <-- FIX 1: INJETAR DB
    emb = None
    if feedback.liked:
        last_recs = get_session(feedback.user_id).get("last_recs", [])
        found = next((i for i in last_recs if i.get("id") == feedback.item_id), None)
        if found:
            emb = await embed_text(f"{found.get('title')} {found.get('description', '')}")
            
    fb = Feedback(user_id=feedback.user_id, item_id=feedback.item_id, liked=feedback.liked, embedding=emb)
    
    # FIX 2: PASSAR O OBJETO DB PARA A FUNÇÃO
    save_feedback(db=db, fb=fb) 
    
    return {"status": "ok", "saved": feedback}

# Endpoints de perfil (CORRIGIDOS: Agora injetam DB e chamam as funções com 'db')
@app.post("/profile/create")
async def create_profile(req: ProfileRequest, db: Session = Depends(get_db)): # <-- INJETAR DB
    # PASSAR O OBJETO DB
    save_profile(db=db, user_id=req.user_id, name=req.name, preferences=req.preferences) 
    return {"status": "ok", "message": f"Perfil '{req.name}' criado!"}

@app.post("/profile/activate")
async def activate_profile(req: ProfileRequest, db: Session = Depends(get_db)): # <-- INJETAR DB
    # A função load_profiles também precisa do DB, mas ela não está
    # sendo importada aqui. Vamos usar a função get_profile_by_name, que é mais direta.
    
    # PASSAR O OBJETO DB
    profile_model = get_profile_by_name(db=db, user_id=req.user_id, name=req.name)
    
    if not profile_model:
        raise HTTPException(status_code=404, detail=f"Perfil '{req.name}' não encontrado.")
    
    # Converte o modelo do SQLAlchemy de volta para um dict para salvar na sessão
    profile_data = {
        "name": profile_model.name,
        "preferences": profile_model.preferences
    }
    
    set_session(req.user_id, {"profile": profile_data})
    return {"status": "ok", "message": f"Perfil '{req.name}' ativado."}

# Endpoint de playlist (NÃO precisa de DB)
@app.post("/playlist")
async def create_playlist(req: PlaylistRequest):
    recs = await recommend(req.preferences, limit=req.limit, user_id=req.user_id)
    playlist_items = await generate_playlist([r.item for r in recs], target_total_minutes=req.target_minutes)
    total = sum([it.duration_minutes or 0 for it in playlist_items])
    return {
        "playlist": [{"title": it.title, "url": it.url, "duration_minutes": it.duration_minutes} for it in playlist_items],
        "total_minutes": total
    }
