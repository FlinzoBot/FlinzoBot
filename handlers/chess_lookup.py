import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_CHESS_USERNAME = range(1)

async def chess_lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your Chess.com username:")
    return ASK_CHESS_USERNAME

async def handle_chess_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().lower()
    base_url = f"https://api.chess.com/pub/player/{username}"
    
    response = requests.get(base_url)
    if response.status_code != 200:
        await update.message.reply_text("No such user was found or an error occurred..")
        return ConversationHandler.END

    profile = response.json()
    stats_url = f"{base_url}/stats"
    stats_response = requests.get(stats_url)

    if stats_response.status_code != 200:
        await update.message.reply_text("Failed to get player stats.")
        return ConversationHandler.END

    stats = stats_response.json()

    blitz = stats.get("chess_blitz", {}).get("last", {})
    rapid = stats.get("chess_rapid", {}).get("last", {})
    bullet = stats.get("chess_bullet", {}).get("last", {})

    info = (
        f"*{profile.get('username', username)}*\n"
        f"- Status: {'aktywny' if profile.get('status') == 'premium' else 'zwykły'}\n"
        f"- Country: {profile.get('country', '').split('/')[-1]}\n"
        f"- Account created at: {profile.get('joined', 'N/A')}\n"
        f"\n"
        f"*Ranking Blitz*: {blitz.get('rating', 'N/A')}\n"
        f"*Ranking Rapid*: {rapid.get('rating', 'N/A')}\n"
        f"*Ranking Bullet*: {bullet.get('rating', 'N/A')}\n"
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
