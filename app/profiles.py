import json, os
from typing import Dict
from app.schemas import Preferences
FILE = "data/profiles.json"
os.makedirs("data", exist_ok=True)
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({}, f)
def save_profile(user_id: str, profile_name: str, prefs: dict):
    with open(FILE, "r") as f:
        data = json.load(f)
    data.setdefault(user_id, {})[profile_name] = prefs
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
def load_profiles(user_id: str) -> Dict:
    with open(FILE, "r") as f:
        data = json.load(f)
    return data.get(user_id, {})
