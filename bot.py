import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler,
    MessageHandler, Filters
)

from license_manager import get_user_license_info
from credit_utils import get_credit_balance, deduct_credit
from throttle_utils import is_throttled
from referral_utils import handle_referral_start
from feedback_utils import save_feedback
from leaderboard_utils import track_usage
from gift_utils import handle_gift_command
from broadcast_utils import daily_broadcast_job

def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "User"
    handle_referral_start(update)

    keyboard = [
        [InlineKeyboardButton("Buy License", callback_data="menu_buy")],
        [InlineKeyboardButton("Perks", callback_data="menu_perks")],
        [InlineKeyboardButton("Credits", callback_data="menu_credits")]
    ]
    update.message.reply_text(
        f"👋 Welcome, {username}!\nReady to unlock premium access?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def buy(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Basic - RM3", callback_data="buy_Basic")],
        [InlineKeyboardButton("Super - RM10", callback_data="buy_Super")],
        [InlineKeyboardButton("Premium - RM15", callback_data="buy_Premium")]
    ]
    update.message.reply_text("🛒 Choose your license:", reply_markup=InlineKeyboardMarkup(keyboard))

def perks(update: Update, context: CallbackContext):
    update.message.reply_text(
        "*License Perks:*\n\n"
        "🧩 *Basic*: 5 msgs/mo, 20s throttle\n"
        "🚀 *Super*: 50 msgs/mo, 10s throttle\n"
        "👑 *Premium*: Unlimited, no throttle",
        parse_mode="Markdown"
    )

def credits(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    bal = get_credit_balance(user_id)
    update.message.reply_text(f"💳 You have *{bal}* credits remaining.", parse_mode="Markdown")

def feedback(update: Update, context: CallbackContext):
    if not context.args or not context.args[0].isdigit():
        return update.message.reply_text("Usage: /feedback <1-5> Your message")
    rating = int(context.args[0])
    comment = " ".join(context.args[1:])
    save_feedback(update.message.from_user.id, rating, comment)
    update.message.reply_text("✅ Thank you for your feedback!")

def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    throttled, wait = is_throttled(user_id)
    if throttled:
        return update.message.reply_text(f"⏳ Please wait {wait}s before sending again.")

    if not deduct_credit(user_id):
        return update.message.reply_text("❌ Out of credits. Use /topup.")

    track_usage(user_id)
    update.message.reply_text("✅ Message received and credit deducted.")

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith("menu_"):
        if data == "menu_buy":
            buy(update, context)
        elif data == "menu_perks":
            perks(update, context)
        elif data == "menu_credits":
            credits(update, context)
    elif data.startswith("buy_"):
        package = data.split("_")[1]
        update.callback_query.edit_message_text(
            f"✅ You selected *{package}*. Proceed to /pay or upload receipt.",
            parse_mode="Markdown"
        )
        # Save package for approval flow

def main():
    updater = Updater(os.getenv("BOT_TOKEN"))
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CommandHandler("perks", perks))
    dp.add_handler(CommandHandler("credits", credits))
    dp.add_handler(CommandHandler("feedback", feedback))
    dp.add_handler(CommandHandler("gift", handle_gift_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(CallbackQueryHandler(handle_callback))

    updater.job_queue.run_daily(daily_broadcast_job, time=datetime.time(hour=10, minute=0))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
