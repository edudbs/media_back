import json, os
from typing import List, Dict
from app.feedback import Feedback
FILE = "data/feedback.json"
os.makedirs("data", exist_ok=True)
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump([], f)
def save_feedback(entry: Feedback):
    with open(FILE, "r") as f:
        data = json.load(f)
    data.append(entry.dict())
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)
def load_feedback(user_id: str) -> List[Dict]:
    with open(FILE, "r") as f:
        all_data = json.load(f)
    return [f for f in all_data if f["user_id"] == user_id]
