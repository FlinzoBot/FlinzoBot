from datetime import datetime

from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_TIMESTAMP = range(1)

async def timestamp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter a date in the format DD.MM.YYYY HH:MM:SS:")
    return ASK_TIMESTAMP

async def handle_timestamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    try:
        dt = datetime.strptime(user_input, "%d.%m.%Y %H:%M:%S")
        unix_timestamp = int(dt.timestamp())

        await update.message.reply_text(
            f"Parsed date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Discord timestamp: `<t:{unix_timestamp}>`\n"
            f"Relative format: `<t:{unix_timestamp}:R>`"
        )
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Incorrect format. Use: DD.MM.YYYY HH:MM:SS (e.g. 04.12.2024 15:13:12)")
        return ASK_TIMESTAMP

timestamp_conversation = ConversationHandler(
    entry_points=[CommandHandler("timestamp", timestamp_command)],
    states={
        ASK_TIMESTAMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_timestamp)],
    },
    fallbacks=[],
)
