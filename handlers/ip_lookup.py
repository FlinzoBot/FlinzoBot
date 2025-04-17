import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_IP = range(1)

async def ip_lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter IP or domain to check:")
    return ASK_IP

async def handle_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip_or_domain = update.message.text.strip()
    url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,message,query,country,regionName,city,zip,lat,lon,isp,org"

    response = requests.get(url)
    data = response.json()

    if data.get("status") == "fail":
        await update.message.reply_text(f"Failed to get information: {data.get('message')}")
        return ConversationHandler.END

    info = (
        f"`{data['query']}`\n"
        f"- Country: {data['country']}\n"
        f"- Region: {data['regionName']}, {data['city']} {data['zip']}\n"
        f"- ISP: {data['isp']} / {data['org']}\n"
        f"- Location: {data['lat']}, {data['lon']}"
    )

    await update.message.reply_text(info, parse_mode="Markdown")
    return ConversationHandler.END

ip_lookup_conversation = ConversationHandler(
    entry_points=[CommandHandler("ip_lookup", ip_lookup_command)],
    states={
        ASK_IP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip)],
    },
    fallbacks=[],
)
