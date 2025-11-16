from openai import OpenAI
from app.config import settings
client = OpenAI(api_key=settings.openai_api_key)
async def embed_text(text: str) -> list:
    res = client.embeddings.create(model="text-embedding-3-small", input=text)
    return res.data[0].embedding
def cosine_similarity(a, b):
    import math
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)
