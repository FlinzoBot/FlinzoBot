import aiohttp
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_HEADER_URL = 0

def is_valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

async def start_headers_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Send me a website URL and I’ll fetch its HTTP headers:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_HEADER_URL

async def handle_headers_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()

    if not is_valid_url(url):
        await update.message.reply_text("Please send a valid URL that starts with http:// or https://")
        return ASK_HEADER_URL

    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=10, allow_redirects=True) as response:
                headers = dict(response.headers)

        if not headers:
            await update.message.reply_text("No headers were returned.")
            return ConversationHandler.END

        formatted = "\n".join([f"*{key}*: {value}" for key, value in headers.items()])
        await update.message.reply_text(
            f"{url}\n\n{formatted[:4000]}",  # Telegram message limit
            parse_mode="Markdown"
        )

    except aiohttp.ClientResponseError as e:
        await update.message.reply_text(f"Client error: {e.status} - {e.message}")
    except aiohttp.ClientError as e:
        await update.message.reply_text(f"Request failed: {e}")
    except Exception as e:
        await update.message.reply_text(f"Unexpected error: {e}")

    return ConversationHandler.END

web_headers_conversation = ConversationHandler(
    entry_points=[CommandHandler("headers_lookup", start_headers_lookup)],
    states={
        ASK_HEADER_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_headers_lookup)],
    },
    fallbacks=[],
)
