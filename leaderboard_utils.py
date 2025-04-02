import json
import os
from collections import Counter

STORAGE_FILE = 'storage.json'

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}, "usage": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def track_usage(user_id):
    """
    Tracks the usage count for a user.
    :param user_id: Telegram user ID
    """
    data = load_storage()
    usage = data.setdefault('usage', {})
    usage[str(user_id)] = usage.get(str(user_id), 0) + 1
    save_storage(data)

def get_leaderboard(top_n=10):
    """
    Retrieves the top N users based on their usage count.
    :param top_n: Number of top users to retrieve
    :return: List of tuples containing user_id and usage count
    """
    data = load_storage()
    usage = data.get('usage', {})
    counter = Counter(usage)
    return counter.most_common(top_n)
