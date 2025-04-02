import json
import os
from datetime import datetime

STORAGE_FILE = 'storage.json'

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_feedback(user_id, rating, comment):
    """
    Saves user feedback with a rating and comment.
    :param user_id: Telegram user ID
    :param rating: Rating provided by the user (e.g., 1 to 5)
    :param comment: Feedback comment
    """
    data = load_storage()
    feedback_entry = {
        'user_id': user_id,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now().isoformat()
    }
    data['feedback'].append(feedback_entry)
    save_storage(data)

def load_feedback():
    """
    Retrieves all feedback entries.
    :return: List of feedback entries
    """
    data = load_storage()
    return data.get('feedback', [])
