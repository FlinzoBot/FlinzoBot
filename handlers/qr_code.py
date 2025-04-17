import qrcode
from io import BytesIO, StringIO

from telegram import Update, InputFile, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_CONTENT = 0

async def start_qr_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args or args[0].lower() not in ["text", "photo"]:
        await update.message.reply_text(
        "Usage: /qr_code text or /qr_code photo\n\n"
        "- `text`: QR code in text form (ASCII)\n"
        "- `photo`: QR code as image"
        )
        return ConversationHandler.END

    qr_format = args[0].lower()
    context.user_data["qr_format"] = qr_format

    await update.message.reply_text("Please enter the text or link for which you want me to generate a QR code:",
                                    reply_markup=ReplyKeyboardRemove())
    return ASK_CONTENT


async def handle_qr_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = update.message.text
    format_choice = context.user_data.get("qr_format")

    if format_choice == "photo":
        qr = qrcode.make(content)
        bio = BytesIO()
        bio.name = "qr_code.png"
        qr.save(bio, "PNG")
        bio.seek(0)
        await update.message.reply_photo(photo=InputFile(bio), caption=f"Here is the QR code for: {content}")
    
    elif format_choice == "text":
        qr = qrcode.QRCode(border=1)
        qr.add_data(content)
        qr.make(fit=True)

        output = StringIO()
        qr.print_ascii(out=output, invert=True)
        output.seek(0)
        qr_text = output.read()

        await update.message.reply_text(
            f"Here is the QR code for: {content}\n\n<pre>{qr_text}</pre>",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text("Format not recognized. I don't know how you got the bot to this state but brag about it on our dc. 😰")
    return ConversationHandler.END


qr_code_conversation = ConversationHandler(
    entry_points=[CommandHandler("qr_code", start_qr_code)],
    states={
        ASK_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_qr_generation)],
    },
    fallbacks=[],
)
