import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_DOMAIN = range(1)

async def domain_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter the domain to check (e.g. google.com):")
    return ASK_DOMAIN

async def handle_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.strip().lower()
    url = f"https://rdap.org/domain/{domain}"

    response = requests.get(url)
    if response.status_code != 200:
        await update.message.reply_text(f"Failed to retrieve domain information: {domain}")
        return ConversationHandler.END

    data = response.json()

    name = data.get("ldhName", "N/A")
    registrar = data.get("registrar", {}).get("name", "N/A")
    statuses = ", ".join(data.get("status", [])) or "N/A"
    events = {e["eventAction"]: e["eventDate"] for e in data.get("events", [])}
    created = events.get("registration", "N/A")
    updated = events.get("last changed", "N/A")
    expires = events.get("expiration", "N/A")

    info = (
        f"`{name}`\n"
        f"- Registrar: {registrar}\n"
        f"- Statuses: {statuses}\n"
        f"- Registration: {created}\n"
        f"- Last change: {updated}\n"
        f"- Expires: {expires}"
    )

    await update.message.reply_text(info, parse_mode="Markdown")
    return ConversationHandler.END

domain_info_conversation = ConversationHandler(
    entry_points=[CommandHandler("domain_info", domain_info_command)],
    states={
        ASK_DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_domain)],
    },
    fallbacks=[],
)
