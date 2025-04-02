from telegram import Update
from telegram.ext import CallbackContext
from license_manager import assign_license, revoke_license_key, load_storage, save_storage
from credit_utils import process_topup_payment
from feedback_utils import load_feedback
from broadcast_utils import send_broadcast_message

ADMIN_ID = "your_telegram_user_id"  # replace with your actual Telegram user ID

def is_admin(user_id):
    return str(user_id) == ADMIN_ID

def handle_panel(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id):
        return update.message.reply_text("Not authorized.")
    update.message.reply_text(
        "/genkey <user_id> <package>\n"
        "/revoke <license_key>\n"
        "/approve <user_id>\n"
        "/approve_topup <user_id>\n"
        "/buyers\n/stats\n/feedbacks\n/broadcast <message>"
    )

def handle_genkey(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id):
        return update.message.reply_text("Not authorized.")
    args = context.args
    if len(args) < 2:
        return update.message.reply_text("Usage: /genkey <user_id> <package>")
    uid, pkg = args[0], args[1]
    key, exp = assign_license(uid, pkg)
    context.bot.send_message(chat_id=int(uid),
        text=f"✅ License issued!\nKey: `{key}`\nExpires: {exp}", parse_mode="Markdown")
    update.message.reply_text(f"License sent to user {uid}")

def handle_revoke(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id):
        return update.message.reply_text("Not authorized.")
    if not context.args:
        return update.message.reply_text("Usage: /revoke <key>")
    if revoke_license_key(context.args[0]):
        update.message.reply_text("✅ License revoked.")
    else:
        update.message.reply_text("License not found.")

def handle_approve(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id): return
    args = context.args
    if not args: return update.message.reply_text("Usage: /approve <user_id>")
    uid = args[0]
    data = load_storage()
    user = data["users"].get(uid)
    if not user: return update.message.reply_text("User not found.")
    pkg = user.get("selected_package", "Basic")
    key, exp = assign_license(uid, pkg)
    context.bot.send_message(chat_id=int(uid),
        text=f"✅ Approved!\nKey: `{key}`\nExpires: {exp}", parse_mode="Markdown")
    update.message.reply_text(f"Approved and sent to {uid}")

def handle_approve_topup(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id): return
    if not context.args: return update.message.reply_text("Usage: /approve_topup <user_id>")
    uid = context.args[0]
    data = load_storage()
    user = data["users"].get(uid)
    if not user or not user.get("topup_pending"):
        return update.message.reply_text("No pending top-up.")
    pkg = user.get("package", "Basic")
    rate = 5 if pkg == "Basic" else 10 if pkg == "Super" else 20
    amount_rm = user["topup_pending"] / rate
    added = process_topup_payment(uid, amount_rm)
    user["topup_pending"] = None
    data["users"][uid] = user
    save_storage(data)
    context.bot.send_message(chat_id=int(uid), text=f"✅ {added} credits added to your account.")
    update.message.reply_text(f"Approved top-up for {uid}.")

def handle_stats(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id): return
    data = load_storage()
    total = len(data["licenses"])
    active = sum(1 for k in data["licenses"].values() if k["active"])
    update.message.reply_text(f"Total: {total}\nActive: {active}")

def handle_buyers(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id): return
    data = load_storage()
    buyers = [f"{uid}: {user.get('package', '-')}" for uid, user in data["users"].items()]
    update.message.reply_text("Buyers:\n" + "\n".join(buyers))

def handle_feedbacks(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id): return
    feedback = load_feedback()
    msg = "\n\n".join([f"{f['user']}: {f['rating']} ⭐\n{f['comment']}" for f in feedback])
    update.message.reply_text(msg or "No feedback yet.")

def handle_broadcast(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id): return
    if not context.args:
        return update.message.reply_text("Usage: /broadcast <message>")
    send_broadcast_message(" ".join(context.args), context.bot)
    update.message.reply_text("📢 Broadcast sent.")
