import re
import time
import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_WEBHOOK, ASK_MESSAGE = range(2)
COOLDOWN_SECONDS = 30

async def webhook_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    last_used = context.user_data.get("last_webhook_time", 0)

    if now - last_used < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_used))
        await update.message.reply_text(f"Cooldown active. Please try again in {remaining} seconds.")
        return ConversationHandler.END

    context.user_data["last_webhook_time"] = now
    await update.message.reply_text("Provide a link to the Discord webhook:")
    return ASK_WEBHOOK



async def handle_webhook_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    pattern = r"^https:\/\/(canary\.|ptb\.)?discord(app)?\.com\/api\/webhooks\/\d+\/[\w-]+$"
    if re.match(pattern, url):
        context.user_data["webhook_url"] = url
        await update.message.reply_text("OK! Now write your message:")
        return ASK_MESSAGE
    else:
        await update.message.reply_text("This doesn't look like a valid link. Please try again:")
        return ASK_WEBHOOK


async def handle_webhook_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    url = context.user_data.get("webhook_url")

    if not url:
        await update.message.reply_text("I forgot your webhook link, start over with the /webhook command!")
        return ConversationHandler.END

    response = requests.post(url, json={"content": message})

    if response.status_code == 204:
        await update.message.reply_text("The message has been sent!")
    else:
        await update.message.reply_text(f"Failed. Response code: {response.status_code}")

    return ConversationHandler.END


webhook_conversation = ConversationHandler(
    entry_points=[CommandHandler("discord_webhook", webhook_command)],
    states={
        ASK_WEBHOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_webhook_link)],
        ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_webhook_message)],
    },
    fallbacks=[],
)
