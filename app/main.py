from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import RecommendRequest, Recommendation, ContentItem, FeedbackRequest, ProfileRequest, PlaylistRequest
from app.recommender import recommend
from app.config import settings
from app.feedback import Feedback
from app.feedback_store import save_feedback
from app.embeddings import embed_text
from app.sessions import set_session, get_session
from app.profiles import save_profile, load_profiles
from app.playlist import generate_playlist

from openai import OpenAI

# -----------------------------------------------------
# 🔒 Validação automática das variáveis de ambiente
# -----------------------------------------------------
REQUIRED_ENV_VARS = {
    "OPENAI_API_KEY": settings.openai_api_key,
    "DATABASE_URL": settings.database_url
}

missing = [key for key, value in REQUIRED_ENV_VARS.items() if not value]

if missing:
    raise RuntimeError(
        f"❌ Environment variables missing: {', '.join(missing)}.\n"
        f"Configure them no .env ou nas variáveis do Render."
    )

# -----------------------------------------------------
# 🔧 Inicialização
# -----------------------------------------------------
client = OpenAI(api_key=settings.openai_api_key)
app = FastAPI(title="Media Recommender API")

# -----------------------------------------------------
# 🌐 CORS — necessário para o front-end do Vercel
# -----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pode trocar depois para seu domínio do Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# 🩺 Health check
# -----------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------------------------------
# 🎬 Rota principal de recomendações
# -----------------------------------------------------
@app.post("/recommend", response_model=list[Recommendation])
async def recommend_endpoint(req: RecommendRequest, user_id: str = "anon", strategy: str = "hybrid"):
    try:
        if strategy == "hybrid":
            from app.hybrid_recommender import hybrid_recommend
            recs = await hybrid_recommend(req.preferences, user_id=user_id, limit=req.limit)
        else:
            recs = await recommend(req.preferences, limit=req.limit, user_id=user_id)

        # salva últimas recomendações na sessão
        set_session(user_id, {"last_recs": [r.item.dict() for r in recs]})
        return recs

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------
# 👍 Feedback do usuário
# -----------------------------------------------------
@app.post("/feedback")
async def post_feedback(feedback: FeedbackRequest):
    emb = None
    if feedback.liked:
        last_recs = get_session(feedback.user_id).get("last_recs", [])
        found = next((i for i in last_recs if i.get("id") == feedback.item_id), None)
        if found:
            emb = await embed_text(f"{found.get('title')} {found.get('description', '')}")

    fb = Feedback(
        user_id=feedback.user_id,
        item_id=feedback.item_id,
        liked=feedback.liked,
        embedding=emb
    )
    save_feedback(fb)
    return {"status": "ok", "saved": feedback}


# -----------------------------------------------------
# 👤 Perfil de usuário
# -----------------------------------------------------
@app.post("/profile/create")
async def create_profile(req: ProfileRequest):
    save_profile(req.user_id, req.name, req.preferences)
    return {"status": "ok", "message": f"Perfil '{req.name}' criado!"}


@app.post("/profile/activate")
async def activate_profile(req: ProfileRequest):
    profiles = load_profiles(req.user_id)
    profile = profiles.get(req.name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{req.name}' não encontrado.")

    set_session(req.user_id, {"profile": profile})
    return {"status": "ok", "message": f"Perfil '{req.name}' ativado."}


# -----------------------------------------------------
# 🎵 Gerar playlist
# -----------------------------------------------------
@app.post("/playlist")
async def create_playlist(req: PlaylistRequest):
    recs = await recommend(req.preferences, limit=req.limit, user_id=req.user_id)
    playlist_items = await generate_playlist([r.item for r in recs], target_total_minutes=req.target_minutes)

    total = sum([it.duration_minutes or 0 for it in playlist_items])
    return {
        "playlist": [{"title": it.title, "url": it.url, "duration_minutes": it.duration_minutes} for it in playlist_items],
        "total_minutes": total
    }
