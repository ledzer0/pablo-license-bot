import json
import os
from telegram import Bot

STORAGE_FILE = 'storage.json'
BOT_TOKEN = os.getenv("BOT_TOKEN")

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}, "usage": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def daily_broadcast_job(context):
    """
    Sends a daily broadcast message to all users.
    """
    data = load_storage()
    bot = Bot(token=BOT_TOKEN)
    message = "Good morning! Here's your daily update."

    for user_id in data['users']:
        try:
            bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")
