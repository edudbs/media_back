import time, json, os
FILE = "data/sessions.json"
os.makedirs("data", exist_ok=True)
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({}, f)
def set_session(user_id: str, data: dict):
    with open(FILE, "r") as f:
        s = json.load(f)
    s[user_id] = {**s.get(user_id, {}), **data, "last_update": time.time()}
    with open(FILE, "w") as f:
        json.dump(s, f, indent=2)
def get_session(user_id: str):
    with open(FILE, "r") as f:
        s = json.load(f)
    return s.get(user_id, {})
def clear_session(user_id: str):
    with open(FILE, "r") as f:
        s = json.load(f)
    if user_id in s:
        del s[user_id]
    with open(FILE, "w") as f:
        json.dump(s, f, indent=2)
