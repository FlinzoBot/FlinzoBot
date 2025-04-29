import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_GITHUB_USER = range(1)

async def github_lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Podaj nazwę użytkownika GitHub:")
    return ASK_GITHUB_USER

async def handle_github_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    url = f"https://api.github.com/users/{username}"

    response = requests.get(url)
    if response.status_code != 200:
        await update.message.reply_text("Nie znaleziono takiego użytkownika GitHub.")
        return ConversationHandler.END

    data = response.json()
    name = data.get("name", username)
    bio = data.get("bio", "Brak opisu")
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    location = data.get("location", "Nie podano")
    created_at = data.get("created_at", "N/A")[:10]
    profile_url = data.get("html_url", f"https://github.com/{username}")

    info = (
        f"*{name}* (`{username}`)\n"
        f"- Location: {location}\n"
        f"- Repos: {public_repos}\n"
        f"- Followers: {followers} | Following: {following}\n"
        f"- Accoount created at: {created_at}\n"
        f"- [Github Profile]({profile_url})\n\n"
        f"- Bio:\n"
        f"_{bio}_"
    )

    await update.message.reply_text(info, parse_mode="Markdown")
    return ConversationHandler.END

github_lookup_conversation = ConversationHandler(
    entry_points=[CommandHandler("github_lookup", github_lookup_command)],
    states={
        ASK_GITHUB_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_github_user)],
    },
    fallbacks=[],
)
