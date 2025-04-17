from telegram import Update
from telegram.ext import ContextTypes

def handle_response(text: str) -> str:
    return "hey"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    if message_type == "group":
        if "@FlinzoBot" in text:
            new_text = text.replace("@FlinzoBot", "").strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)

    await update.message.reply_text(response)
