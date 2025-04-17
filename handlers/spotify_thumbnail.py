from io import BytesIO
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from telegram import InputFile, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

ASK_SPOTIFY_URL = 0

def is_valid_spotify_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc in {"open.spotify.com"} and parsed.path.startswith(("/track/", "/album/"))

async def start_spotify_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please send a Spotify song or album link and I will fetch its cover art for you:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_SPOTIFY_URL

async def handle_spotify_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    spotify_url = update.message.text.strip()

    if not is_valid_spotify_url(spotify_url):
        await update.message.reply_text("This is not a valid Spotify track or album URL. Try again.")
        return ASK_SPOTIFY_URL

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(spotify_url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        meta = soup.find("meta", property="og:image")
        if not meta or not meta["content"]:
            await update.message.reply_text("Could not find cover art in the page metadata.")
            return ASK_SPOTIFY_URL

        image_url = meta["content"]

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=10) as img_response:
                img_response.raise_for_status()
                content = await img_response.read()

        bio = BytesIO(content)
        bio.name = "spotify_cover.jpg"
        bio.seek(0)

        await update.message.reply_photo(
            photo=InputFile(bio),
            caption=f"Here's the Spotify cover art for:\n{spotify_url}",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

    return ConversationHandler.END


spotify_thumbnail_conversation = ConversationHandler(
    entry_points=[CommandHandler("spotify_thumbnail", start_spotify_thumbnail)],
    states={
        ASK_SPOTIFY_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_spotify_thumbnail)],
    },
    fallbacks=[],
)
