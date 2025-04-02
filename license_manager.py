import json
import os
import uuid
from datetime import datetime, timedelta

STORAGE_FILE = 'storage.json'

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_license_key():
    return str(uuid.uuid4())

def assign_license(user_id, package):
    data = load_storage()
    license_key = generate_license_key()
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    data['licenses'][license_key] = {
        'user_id': user_id,
        'package': package,
        'expiry_date': expiry_date,
        'active': True
    }
    data['users'][user_id] = {
        'license_key': license_key,
        'package': package,
        'expiry_date': expiry_date
    }
    save_storage(data)
    return license_key, expiry_date

def get_user_license_info(user_id):
    data = load_storage()
    user = data['users'].get(user_id)
    if not user:
        return None, None, None
    return user['license_key'], user['package'], user['expiry_date']

def verify_license(license_key):
    data = load_storage()
    license_info = data['licenses'].get(license_key)
    if not license_info or not license_info['active']:
        return False, None, None
    return True, license_info['package'], license_info['expiry_date']

def revoke_license_key(license_key):
    data = load_storage()
    if license_key in data['licenses']:
        data['licenses'][license_key]['active'] = False
        user_id = data['licenses'][license_key]['user_id']
        if user_id in data['users']:
            del data['users'][user_id]
        save_storage(data)
        return True
    return False
