import json
import os

STORAGE_FILE = 'storage.json'

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_credit_balance(user_id):
    data = load_storage()
    user = data['users'].get(str(user_id))
    if not user:
        return 0
    return user.get('credits', 0)

def deduct_credit(user_id, amount=1):
    data = load_storage()
    user = data['users'].get(str(user_id))
    if not user or user.get('credits', 0) < amount:
        return False
    user['credits'] -= amount
    save_storage(data)
    return True

def add_credits(user_id, amount):
    data = load_storage()
    user = data['users'].setdefault(str(user_id), {})
    user['credits'] = user.get('credits', 0) + amount
    save_storage(data)

def process_topup_payment(user_id, amount_rm):
    """
    Process a top-up payment and add credits to the user's account.
    :param user_id: Telegram user ID
    :param amount_rm: Amount in Ringgit Malaysia (RM)
    :return: Number of credits added
    """
    data = load_storage()
    user = data['users'].get(str(user_id))
    if not user:
        return 0

    package = user.get('package', 'Basic')
    rate = {'Basic': 5, 'Super': 10, 'Premium': 20}.get(package, 5)
    credits_to_add = int(amount_rm * rate)
    user['credits'] = user.get('credits', 0) + credits_to_add
    save_storage(data)
    return credits_to_add
