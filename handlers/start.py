from telegram import Update
from telegram.ext import ContextTypes

header = "Hi, I'm FlinzoBot - open source bot on Telegram offering a wide range of tools for websites, discord, math and more. Below you will find my commands :3"

help = """
General Commands:
/help - Show this help message with all available commands
/start - Start interacting with the bot

Discord Tools:
/discord_webhook - Send a webhook message to Discord
/timestamp - Convert a date to a Discord timestamp

Website Tools:
/headers_lookup - Retrieve HTTP headers from a given URL
/meta_tags_lookup - Retrieve meta tags from a given URL
/ip_lookup - Get IP address information
/domain_info - Get domain information
/dns_lookup - Get DNS records for a given domain
/ssl_info - Get SSL certificate information
 
Text Tools:
/len - Count the number of characters in a given text
/random_number - Generate a random number from a given range
/cipher - Encrypt or decrypt a given text
/morse - Encode or decode Morse code

Other Tools:
/mc_lookup - Get information about a Minecraft server
/chess_lookup - Get information about a chess.com player
/github_lookup - Get information about github user
/reddit_lookup - Get information about a reddit user
/spotify_thumbnail - Get the thumbnail from a Spotify URL
/youtube_thumbnail - Get the thumbnail from a YouTube URL
/qr_code - Generate a QR code from a given text or link
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(F"{header}\n\n{help}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(F"{header}\n\n{help}")
