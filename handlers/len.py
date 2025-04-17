from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_MSG = range(1)

async def len_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args or args[0].lower() not in ["with", "without"]:
        await update.message.reply_text(
        "Usage: /len with or /len without\n\n"
        "- `with`: Counting number of characters including spaces\n"
        "- `without`: Counting number of characters excluding spaces"
        )
        return ConversationHandler.END

    len_format = args[0].lower()
    context.user_data["len_format"] = len_format

    await update.message.reply_text("Enter the text whose characters you want me to count.:",
                                    reply_markup=ReplyKeyboardRemove())
    return ASK_MSG

async def handle_len(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    choice = context.user_data.get("len_format")

    if choice == "with":
        char_count = len(text)
        await update.message.reply_text(f"The number of characters in the text is: {char_count}")

    elif choice == "without":
        char_count = len(text.replace(" ", ""))
        await update.message.reply_text(f"The number of characters in the text without spaces is: {char_count}")

    return ConversationHandler.END


    

len_conversation = ConversationHandler(
    entry_points=[CommandHandler("len", len_command)],
    states={
        ASK_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_len)],
    },
    fallbacks=[],
)
