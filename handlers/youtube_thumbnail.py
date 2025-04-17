import re
from io import BytesIO
from urllib.parse import parse_qs, urlparse

import aiohttp
from telegram import InputFile, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

ASK_VIDEO_URL = 0

def extract_video_id(url: str) -> str | None:
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in {"youtu.be"}:
            return parsed_url.path[1:]
        elif "youtube" in parsed_url.hostname:
            query = parse_qs(parsed_url.query)
            video_id = query.get("v", [None])[0]
            if video_id:
                return video_id
            return parsed_url.path.split("/")[2] if len(parsed_url.path.split("/")) > 2 else None
    except (ValueError, IndexError) as e:
        print(f"Error extracting video ID: {e}")
        return None

def is_valid_youtube_url(url: str) -> bool:
    regex = r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$"
    return re.match(regex, url) is not None

async def start_thumbnail_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please send a YouTube video link and I will fetch its thumbnail for you:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_VIDEO_URL

async def handle_thumbnail_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video_url = update.message.text.strip()

    if not is_valid_youtube_url(video_url):
        await update.message.reply_text("The link you provided is not a valid YouTube URL. Please try again.")
        return ASK_VIDEO_URL 

    video_id = extract_video_id(video_url)

    if not video_id:
        await update.message.reply_text("Unable to extract the video ID. Please make sure the URL is correct and try again.")
        return ASK_VIDEO_URL 

    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url, timeout=10) as response:
                response.raise_for_status()  
                content = await response.read()

        bio = BytesIO(content)
        bio.name = f"thumbnail_{video_id}.jpg"
        bio.seek(0)

        await update.message.reply_photo(
            photo=InputFile(bio),
            caption=f"Here's the thumbnail for the video:\n{video_url}",
            reply_markup=ReplyKeyboardRemove()
        )
    except aiohttp.ClientError as e:
        await update.message.reply_text(f"An error occurred while downloading the thumbnail:\n{e}")
    except Exception as e:
        await update.message.reply_text(f"An unexpected error occurred:\n{e}")

    return ConversationHandler.END


yt_thumbnail_conversation = ConversationHandler(
    entry_points=[CommandHandler("youtube_thumbnail", start_thumbnail_download)],
    states={
        ASK_VIDEO_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_thumbnail_download)],
    },
    fallbacks=[], 
)
