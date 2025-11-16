async def generate_playlist(items, target_total_minutes: int = 90):
    playlist = []
    total = 0
    for it in items:
        if it.duration_minutes:
            if total + it.duration_minutes > target_total_minutes:
                continue
        playlist.append(it)
        if it.duration_minutes:
            total += it.duration_minutes
        if total >= target_total_minutes:
            break
    return playlist
