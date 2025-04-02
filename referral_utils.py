import json
import os
from urllib.parse import urlencode

STORAGE_FILE = 'storage.json'
BOT_USERNAME = os.getenv("BOT_USERNAME")  # e.g., 'YourBotUsername'

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_referral_link(user_id):
    """
    Generates a unique referral link for the user.
    :param user_id: Telegram user ID
    :return: Referral link as a string
    """
    params = {'start': f'ref{user_id}'}
    referral_link = f"https://t.me/{BOT_USERNAME}?{urlencode(params)}"
    return referral_link

def handle_referral_start(update):
    """
    Handles the start command with referral parameter.
    :param update: Telegram update object
    """
    user_id = str(update.message.from_user.id)
    args = update.message.text.split()
    if len(args) > 1 and args[1].startswith('ref'):
        referrer_id = args[1][3:]
        if referrer_id != user_id:  # Prevent self-referral
            data = load_storage()
            referrals = data.setdefault('referrals', {})
            user_referrals = referrals.setdefault(referrer_id, [])
            if user_id not in user_referrals:
                user_referrals.append(user_id)
                save_storage(data)

def get_referral_count(user_id):
    """
    Retrieves the number of referrals made by the user.
    :param user_id: Telegram user ID
    :return: Number of referrals
    """
    data = load_storage()
    referrals = data.get('referrals', {})
    user_referrals = referrals.get(str(user_id), [])
    return len(user_referrals)
