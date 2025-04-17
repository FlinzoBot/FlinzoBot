import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

ASK_MC_SERVER = range(1)

async def mc_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Provide the IP or domain of your Minecraft server:")
    return ASK_MC_SERVER

async def handle_mc_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    url = f"https://api.mcsrvstat.us/2/{address}"

    response = requests.get(url)
    if response.status_code != 200:
        await update.message.reply_text("Failed to retrieve server data.")
        return ConversationHandler.END

    data = response.json()
    
    if not data.get("online"):
        await update.message.reply_text("The server is offline or does not exist.")
        return ConversationHandler.END

    ip = data.get("ip", "N/A")
    port = data.get("port", "N/A")
    hostname = data.get("hostname", address)
    version = data.get("version", "N/A")
    players = data.get("players", {})
    online = players.get("online", 0)
    max_players = players.get("max", 0)
    motd = "\n".join(data.get("motd", {}).get("clean", [])) or "N/A"

    info = (
        f"`{hostname}`\n"
        f"- IP: {ip}:{port}\n"
        f"- Version: {version}\n"
        f"- Players: {online}/{max_players}\n"
        f"- MOTD:\n{motd}"
    )

    await update.message.reply_text(info, parse_mode="Markdown")
    return ConversationHandler.END

mc_info_conversation = ConversationHandler(
    entry_points=[CommandHandler("mc_lookup", mc_info_command)],
    states={
        ASK_MC_SERVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mc_server)],
    },
    fallbacks=[],
)
