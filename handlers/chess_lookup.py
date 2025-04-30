import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

ASK_CHESS_USERNAME = 0

async def chess_lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter your Chess.com username:")
    return ASK_CHESS_USERNAME

async def handle_chess_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("Couldn't read the username. Please try again.")
        return ConversationHandler.END

    username = update.message.text.strip().lower()
    base_url = f"https://api.chess.com/pub/player/{username}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TelegramBot/1.0)"} # The chess.com API requires us to send an headers with a User-Agent

    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        await update.message.reply_text(f"User '{username}' not found.")
        return ConversationHandler.END

    profile = response.json()

    stats_url = f"{base_url}/stats"
    stats_response = requests.get(stats_url, headers=headers)
    if stats_response.status_code != 200:
        await update.message.reply_text("Failed to retrieve player stats.")
        return ConversationHandler.END

    stats = stats_response.json()

    blitz = stats.get("chess_blitz", {})
    rapid = stats.get("chess_rapid", {})
    bullet = stats.get("chess_bullet", {})
    puzzle = stats.get("tactics", {})

    def total_games(mode):
        record = mode.get("record", {})
        return record.get("win", 0) + record.get("loss", 0) + record.get("draw", 0)

    joined_ts = profile.get("joined")
    joined_date = datetime.utcfromtimestamp(joined_ts).strftime('%Y-%m-%d') if joined_ts else 'N/A'

    title = profile.get("title", "").upper()
    display_name = f"{title} {profile.get('username', username)}" if title else profile.get('username', username)

    country_code = profile.get("country", "").split("/")[-1].upper()

    blitz_games = total_games(blitz)
    rapid_games = total_games(rapid)
    bullet_games = total_games(bullet)
    puzzles_solved = puzzle.get("highest", {}).get("rating", "N/A")

    info = (
        f"**[{display_name}](https://www.chess.com/member/{username})**\n"
        f"- Country: {country_code}\n"
        f"- Title: {title or 'None'}\n"
        f"- Account status: {profile.get('status', 'N/A')}\n"
        f"- Account created on: {joined_date}\n\n"

        f"**Ranking:**\n"
        f"- *Blitz*: {blitz.get('last', {}).get('rating', 'N/A')} ({blitz_games} games)\n"
        f"- *Rapid*: {rapid.get('last', {}).get('rating', 'N/A')} ({rapid_games} games)\n"
        f"- *Bullet*: {bullet.get('last', {}).get('rating', 'N/A')} ({bullet_games} games)\n"
        f"- *Puzzles*: {puzzles_solved}\n"
    )

    await update.message.reply_text(info, parse_mode="Markdown")
    return ConversationHandler.END

chess_lookup_conversation = ConversationHandler(
    entry_points=[CommandHandler("chess_lookup", chess_lookup_command)],
    states={
        ASK_CHESS_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chess_username)],
    },
    fallbacks=[],
)
