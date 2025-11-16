import httpx
from typing import List
from app.config import settings
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
async def search_youtube(query: str, max_results: int = 5) -> List[dict]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": settings.youtube_api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(YOUTUBE_SEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()
    items = []
    video_ids = [i["id"]["videoId"] for i in data.get("items", []) if i.get('id') and i['id'].get('videoId')]
    if not video_ids:
        return []
    params2 = {"part": "snippet,contentDetails", "id": ",".join(video_ids), "key": settings.youtube_api_key}
    async with httpx.AsyncClient(timeout=15) as client:
        r2 = await client.get(YOUTUBE_VIDEO_URL, params=params2)
        r2.raise_for_status()
        details = r2.json()
    for it in details.get("items", []):
        duration = it.get("contentDetails", {}).get("duration","")
        minutes = None
        try:
            s = duration.replace("PT", "")
            if "H" in s:
                h, rest = s.split("H")
                minutes = int(h) * 60
                s = rest
            if "M" in s:
                m = s.split("M")[0]
                minutes = (minutes or 0) + int(m)
        except Exception:
            minutes = None
        items.append({
            "id": it["id"],
            "title": it.get("snippet",{}).get("title"),
            "description": it.get("snippet",{}).get("description"),
            "platform": "youtube",
            "url": f"https://www.youtube.com/watch?v={it['id']}",
            "duration_minutes": minutes,
            "metadata": {"channelTitle": it.get("snippet",{}).get("channelTitle")}
        })
    return items
