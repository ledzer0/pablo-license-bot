import json
import os
from telegram import Update
from telegram.ext import CallbackContext
from license_manager import assign_license

STORAGE_FILE = 'storage.json'

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"licenses": {}, "users": {}, "feedback": [], "referrals": {}}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def handle_gift_command(update: Update, context: CallbackContext):
    """
    Handles the /gift command to allow users to gift licenses to others.
    Usage: /gift <recipient_user_id> <package>
    """
    if len(context.args) != 2:
        update.message.reply_text("Usage: /gift <recipient_user_id> <package>")
        return

    giver_id = str(update.message.from_user.id)
    recipient_id, package = context.args

    data = load_storage()
    giver = data['users'].get(giver_id)

    if not giver:
        update.message.reply_text("❌ You don't have an active license to gift.")
        return

    # Optional: Check if the giver has gifting rights or sufficient credits
    # For example, only Premium users can gift, or gifting costs credits

    # Assign the license to the recipient
    license_key, expiry_date = assign_license(recipient_id, package)
    context.bot.send_message(
        chat_id=int(recipient_id),
        text=f"🎁 You've received a {package} license as a gift!\n"
             f"License Key: `{license_key}`\n"
             f"Expires on: {expiry_date}",
        parse_mode="Markdown"
    )
    update.message.reply_text(f"✅ Successfully gifted a {package} license to user {recipient_id}.")

    # Optional: Log the gifting action
    # gifting_log = data.setdefault('gifting_log', [])
    # gifting_log.append({
    #     'giver_id': giver_id,
    #     'recipient_id': recipient_id,
    #     'package': package,
    #     'timestamp': datetime.now().isoformat()
    # })
    # save_storage(data)
