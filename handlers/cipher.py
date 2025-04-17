from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_SHIFT, ASK_TEXT = range(2)

def caesar_cipher(text, shift, mode="encrypt"):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            if mode == "encrypt":
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += chr((ord(char) - base - shift) % 26 + base)
        else:
            result += char
    return result

async def cipher_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args or args[0].lower() not in ["encrypt", "decrypt"]:
        await update.message.reply_text(
            "Usage: /cipher encrypt or /cipher decrypt\n\n"
            "- `encrypt`: Encrypt text using Caesar cipher\n"
            "- `decrypt`: Decrypt text using Caesar cipher"
        )
        return ConversationHandler.END

    mode = args[0].lower()
    context.user_data["cipher_mode"] = mode

    await update.message.reply_text("Enter the shift value (a number):",
                                    reply_markup=ReplyKeyboardRemove())
    return ASK_SHIFT

async def ask_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        shift = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number for the shift.")
        return ASK_SHIFT

    context.user_data["cipher_shift"] = shift
    await update.message.reply_text("Now enter the text:")
    return ASK_TEXT

async def handle_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mode = context.user_data.get("cipher_mode")
    shift = context.user_data.get("cipher_shift")

    result = caesar_cipher(text, shift, mode)

    await update.message.reply_text(f"The result is:\n{result}")
    return ConversationHandler.END

cipher_conversation = ConversationHandler(
    entry_points=[CommandHandler("cipher", cipher_command)],
    states={
        ASK_SHIFT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_text)],
        ASK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cipher)],
    },
    fallbacks=[],
)
