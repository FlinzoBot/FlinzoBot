import time
from datetime import datetime

import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

ASK_SSL_DOMAIN = range(1)

async def ssl_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter the domain to check SSL info (e.g. google.com):")
    return ASK_SSL_DOMAIN

def fetch_ssl_info(domain: str):
    api_url = "https://api.ssllabs.com/api/v3/analyze"
    try:
        requests.get(api_url, params={"host": domain, "all": "done", "startNew": "on"})

        for _ in range(15):  # max ~75 seconds
            time.sleep(5)
            response = requests.get(api_url, params={"host": domain, "all": "done"})
            if response.status_code != 200:
                return f"Failed to connect to SSL Labs API for `{domain}`."

            data = response.json()
            status = data.get("status")

            if status == "READY":
                endpoint = data["endpoints"][0]
                grade = endpoint.get("grade", "N/A")

                cert = endpoint.get("details", {}).get("cert", {})
                issued_to = cert.get("commonNames", ["N/A"])[0]
                issued_by = cert.get("issuerLabel", "N/A")
                valid_from = cert.get("notBefore", 0)
                valid_to = cert.get("notAfter", 0)

                valid_from_dt = datetime.utcfromtimestamp(valid_from)
                valid_to_dt = datetime.utcfromtimestamp(valid_to)
                days_left = (valid_to_dt - datetime.utcnow()).days

                return (
                    f"**{domain}**\n"
                    f"- Grade: {grade}\n"
                    f"- Issued To: {issued_to}\n"
                    f"- Issued By: {issued_by}\n"
                    f"- Valid From: {valid_from_dt.strftime('%Y-%m-%d')}\n"
                    f"- Valid To: {valid_to_dt.strftime('%Y-%m-%d')}\n"
                    f"- Days Until Expiry: {days_left}"
                )

            elif status == "ERROR":
                return f"SSL Labs analysis failed for `{domain}`."

        return f"Timeout while waiting for analysis result for `{domain}`. Try again later."

    except Exception as e:
        return f"Error while fetching SSL info: {e}"

async def handle_ssl_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.strip().lower()
    await update.message.reply_text("Analyzing SSL certificate, please wait a few seconds...")
    info = fetch_ssl_info(domain)
    await update.message.reply_text(info, parse_mode="Markdown")
    return ConversationHandler.END

ssl_info_conversation = ConversationHandler(
    entry_points=[CommandHandler("ssl_info", ssl_info_command)],
    states={
        ASK_SSL_DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ssl_domain)],
    },
    fallbacks=[],
)
