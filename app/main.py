from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from app.schemas import RecommendRequest, Recommendation, ContentItem
from app.recommender import recommend
from app.config import settings
from openai import OpenAI
from app.feedback import Feedback
from app.feedback_store import save_feedback
from app.embeddings import embed_text
from app.sessions import set_session, get_session
from app.profiles import save_profile, load_profiles
client = OpenAI(api_key=settings.openai_api_key)
app = FastAPI(title="Media Recommender API")
@app.get("/health")
async def health():
    return {"status": "ok"}
@app.post("/recommend", response_model=list[Recommendation])
async def recommend_endpoint(req: RecommendRequest, user_id: str = "anon", strategy: str = "hybrid"):
    try:
        if strategy == "hybrid":
            from app.hybrid_recommender import hybrid_recommend
            recs = await hybrid_recommend(req.preferences, user_id=user_id, limit=req.limit)
        else:
            recs = await recommend(req.preferences, limit=req.limit, user_id=user_id)
        # save last recommendations to session
        set_session(user_id, {"last_recs": [r.item.dict() for r in recs]})
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/feedback")
async def post_feedback(feedback: Feedback):
    save_feedback(feedback)
    return {"status": "ok", "saved": feedback}
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    incoming_msg = form.get("Body", "").strip()
    from_number = form.get("From", "anon")
    user_id = from_number
    # simple command parsing for feedback and playlist/profile commands
    toks = incoming_msg.lower().split()
    # feedback patterns: 'gostei <id>' or 'nao gostei <id>'
    if len(toks) >= 2 and toks[0] in ["gostei","curti","like"]:
        item_id = toks[1]
        # try to find last recommended item with that id to capture embedding
        sess = get_session(user_id)
        last = sess.get("last_recs", [])
        found = next((i for i in last if i.get("id") == item_id), None)
        emb = None
        if found:
            emb = await embed_text(f"{found.get('title')} {found.get('description','')}")
        fb = Feedback(user_id=user_id, item_id=item_id, liked=True, embedding=emb)
        save_feedback(fb)
        return PlainTextResponse("<Response><Message>Obrigado! Vou ajustar suas recomendações 😊</Message></Response>", media_type="application/xml")
    if len(toks) >= 2 and toks[0] in ["nao","não","nao gostei","dislike"]:
        item_id = toks[1]
        fb = Feedback(user_id=user_id, item_id=item_id, liked=False)
        save_feedback(fb)
        return PlainTextResponse("<Response><Message>Obrigado pelo feedback! Vou evitar conteúdos parecidos 👌</Message></Response>", media_type="application/xml")
    # profile commands: 'criar perfil <nome>: <prefs>' or 'usar perfil <nome>'
    if incoming_msg.lower().startswith("criar perfil"):
        try:
            # format: criar perfil filmes: comédia, ação
            rest = incoming_msg[len("criar perfil"):].strip()
            name, prefs_text = rest.split(":",1)
            name = name.strip()
            # naive parse genres
            genres = [g.strip() for g in prefs_text.split(",") if g.strip()]
            save_profile(user_id, name, {"genres": genres})
            return PlainTextResponse(f"<Response><Message>Perfil '{name}' salvo.</Message></Response>", media_type="application/xml")
        except Exception:
            return PlainTextResponse("<Response><Message>Formato inválido. Use: criar perfil NOME: genero1, genero2</Message></Response>", media_type="application/xml")
    if incoming_msg.lower().startswith("usar perfil"):
        try:
            name = incoming_msg[len("usar perfil"):].strip()
            profiles = load_profiles(user_id)
            p = profiles.get(name)
            if not p:
                return PlainTextResponse(f"<Response><Message>Perfil '{name}' não encontrado.</Message></Response>", media_type="application/xml")
            set_session(user_id, {"profile": p})
            return PlainTextResponse(f"<Response><Message>Perfil '{name}' ativado.</Message></Response>", media_type="application/xml")
        except Exception:
            return PlainTextResponse("<Response><Message>Erro ao ativar perfil.</Message></Response>", media_type="application/xml")
    # playlist command: 'playlist 60min comédia'
    if incoming_msg.lower().startswith("playlist"):
        toks = incoming_msg.split()
        try:
            mins = int(toks[1].lower().replace("min",""))
        except Exception:
            mins = 60
        query = " ".join(toks[2:]) or "recommended"
        # create simple prefs and call recommender
        from app.schemas import Preferences
        prefs = Preferences(genres=[query])
        recs = await recommend(prefs, limit=20, user_id=user_id)
        from app.playlist import generate_playlist
        playlist = await generate_playlist([r.item for r in recs], target_total_minutes=mins)
        text = "Sua playlist:\n\n"
        total = 0
        for it in playlist:
            text += f"• {it.title} - {it.url or 'link não disponível'}\n"
            if it.duration_minutes:
                total += it.duration_minutes
        text += f"\nTempo total aproximado: {total} minutos"
        return PlainTextResponse(f"<Response><Message>{text}</Message></Response>", media_type="application/xml")
    # if none matched, treat as recommendation request
    from app.schemas import Preferences
    prefs = Preferences(genres=[incoming_msg])
    recs = await recommend(prefs, limit=5, user_id=user_id)
    text = "Aqui estão ótimas recomendações para você:\n\n"
    for r in recs:
        text += f"• {r.item.title} - {r.item.url or '—'}\n{r.why}\n\n"
    # save last recs
    set_session(user_id, {"last_recs": [r.item.dict() for r in recs]})
    return PlainTextResponse(f"<Response><Message>{text}</Message></Response>", media_type="application/xml")
