import asyncio
import socket

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


ASK_DOMAIN = 0

def is_valid_domain(domain: str) -> bool:
    return all(part.isalnum() or part in "-." for part in domain) and "." in domain

async def start_dns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Send me a domain (e.g. `example.com`) and I’ll try to resolve its IP address:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_DOMAIN

async def resolve_basic_dns(domain: str) -> str:
    try:
        loop = asyncio.get_event_loop()
        ipv4s = await loop.run_in_executor(None, lambda: socket.gethostbyname_ex(domain))
        ipv6s = await loop.run_in_executor(None, lambda: socket.getaddrinfo(domain, None, socket.AF_INET6))

        result = [f"*A (IPv4)*: {', '.join(ipv4s[2])}"]

        if ipv6s:
            unique_ipv6 = sorted(set(info[4][0] for info in ipv6s))
            result.append(f"*AAAA (IPv6)*: {', '.join(unique_ipv6)}")

        return "\n".join(result)

    except socket.gaierror:
        return "Could not resolve the domain. It might not exist or DNS is unreachable."
    except Exception as e:
        return f"Error: {e}"

async def handle_dns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    domain = update.message.text.strip().lower()

    if not is_valid_domain(domain):
        await update.message.reply_text("This doesn’t look like a valid domain.")
        return ASK_DOMAIN

    await update.message.reply_text("Resolving domain...")
    result = await resolve_basic_dns(domain)

    await update.message.reply_text(
        f"{domain}:\n\n{result}",
        parse_mode="Markdown"
    )

    return ConversationHandler.END

basic_dns_conversation = ConversationHandler(
    entry_points=[CommandHandler("dns_lookup", start_dns)],
    states={
        ASK_DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dns)],
    },
    fallbacks=[],
)
