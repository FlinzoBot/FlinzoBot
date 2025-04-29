import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_REDDIT_USER = range(1)

async def reddit_lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide the Reddit username (withour 'u/', eg. stainowy):")
    return ASK_REDDIT_USER

async def handle_reddit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    url = f"https://www.reddit.com/user/{username}/about.json"
    response = requests.get(url)
    
    if response.status_code != 200:
        await update.message.reply_text("Failed to access Reddit profile. Make sure it's a valid public profile.")
        return ConversationHandler.END

    data = response.json()
    user_data = data.get("data", {})
    
    if not user_data:
        await update.message.reply_text("Could not retrieve data. Ensure the username is correct and public.")
        return ConversationHandler.END

    username = user_data.get("name", "N/A")
    karma = user_data.get("total_karma", "N/A")
    account_creation = user_data.get("created_utc", "N/A")
    link_karma = user_data.get("link_karma", "N/A")
    comment_karma = user_data.get("comment_karma", "N/A")

    info = (
        f"**{username}**\n"
        f"- Total Karma: {karma}\n"
        f"- Link Karma: {link_karma}\n"
        f"- Comment Karma: {comment_karma}\n"
        f"- Account created at: {account_creation} (Unix timestamp)"
    )

    await update.message.reply_text(info)
    return ConversationHandler.END

reddit_lookup_conversation = ConversationHandler(
    entry_points=[CommandHandler("reddit_lookup", reddit_lookup_command)],
    states={
        ASK_REDDIT_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reddit_user)],
    },
    fallbacks=[],
)
