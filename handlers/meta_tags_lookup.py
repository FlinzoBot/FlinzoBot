import aiohttp
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

ASK_WEBSITE_URL = 0

def is_valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

async def start_meta_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Send me a website URL and I’ll fetch its meta tags:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_WEBSITE_URL

async def handle_meta_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()

    if not is_valid_url(url):
        await update.message.reply_text("Please send a valid URL that starts with http:// or https://")
        return ASK_WEBSITE_URL

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        tags = {}

        if soup.title:
            tags["title"] = soup.title.string.strip()

        for tag in soup.find_all("meta"):
            if tag.get("name"):
                tags[tag.get("name")] = tag.get("content", "")
            elif tag.get("property"):
                tags[tag.get("property")] = tag.get("content", "")

        if not tags:
            await update.message.reply_text("No meta tags were found.")
            return ConversationHandler.END

        formatted = "\n".join([f"*{key}*: {value}" for key, value in tags.items()])

        await update.message.reply_text(
            f"{url}\n\n{formatted[:4000]}",  # Telegram message limit
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"An error occurred while fetching the page:\n{e}")

    return ConversationHandler.END

web_meta_conversation = ConversationHandler(
    entry_points=[CommandHandler("meta_tags_lookup", start_meta_lookup)],
    states={
        ASK_WEBSITE_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_meta_lookup)],
    },
    fallbacks=[],
)
