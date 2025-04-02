import time
import json
import os

STORAGE_FILE = 'storage.json'

# Throttle limits in seconds for each package
THROTTLE_LIMITS = {
    'Basic': 20,
    'Super': 10,
    'Premium': 0  # No throttling for Premium users
}

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_throttled(user_id):
    """
    Checks if the user is sending messages too quickly based on their package.
    :param user_id: Telegram user ID
    :return: (bool, int) - True and wait time if throttled, False and 0 otherwise
    """
    data = load_storage()
    user = data['users'].get(str(user_id))
    if not user:
        return False, 0

    package = user.get('package', 'Basic')
    last_message_time = user.get('last_message_time', 0)
    current_time = time.time()
    throttle_limit = THROTTLE_LIMITS.get(package, 20)

    if throttle_limit == 0:
        return False, 0

    if current_time - last_message_time < throttle_limit:
        wait_time = throttle_limit - (current_time - last_message_time)
        return True, int(wait_time)

    # Update last message time
    user['last_message_time'] = current_time
    save_storage(data)
    return False, 0
