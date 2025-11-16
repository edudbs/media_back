import httpx
from typing import List
from app.config import settings
TMDB_SEARCH_MOVIE = "https://api.themoviedb.org/3/search/movie"
TMDB_SEARCH_TV = "https://api.themoviedb.org/3/search/tv"
async def search_tmdb(query: str, max_results: int = 5, media_type: str = "movie") -> List[dict]:
    url = TMDB_SEARCH_MOVIE if media_type == "movie" else TMDB_SEARCH_TV
    params = {"api_key": settings.tmdb_api_key, "query": query, "page": 1}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    items = []
    for it in data.get("results", [])[:max_results]:
        items.append({
            "id": f"tmdb-{it.get('id')}",
            "title": it.get("title") or it.get("name"),
            "description": it.get("overview"),
            "platform": "tmdb",
            "url": None,
            "duration_minutes": None,
            "metadata": {"popularity": it.get("popularity"), "release_date": it.get("release_date")}
        })
    return items
