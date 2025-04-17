import random

from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_COUNT = range(1)

async def rng_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter a range of numbers in the format e.g. 10-100:")
    return ASK_COUNT

async def handle_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    range_input = update.message.text.strip().replace(" ", "")

    if range_input.count('-') != 1:
        await update.message.reply_text("Incorrect format. Enter range in format e.g. 10-100.")
        return ASK_COUNT

    try:
        start_str, end_str = range_input.split('-')
        start = int(start_str)
        end = int(end_str)

        if start > end:
            start, end = end, start

        random_number = random.randint(start, end)
        await update.message.reply_text(f"Random number: {random_number}")
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("The range must consist of numbers only, e.g. 10-100.")
        return ASK_COUNT

random_number_conversation = ConversationHandler(
    entry_points=[CommandHandler("random_number", rng_command)],
    states={
        ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_count)],
    },
    fallbacks=[],
)
