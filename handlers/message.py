from telegram import Update
from telegram.ext import ContextTypes

def handle_response(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["hi", "hello", "hey"]):
        return "Hello! Nice to see you. I'm FlinzoBot. To start our adventure use the command /start!"

    if any(word in text for word in ["github", "source", "repo"]):
        return "Hi user, my source code is open and available to everyone. You can check it out on GitHub:\nhttps://github.com/FlinzoBot"

    if any(word in text for word in ["@flinzobot", "flinzobot"]):
        return "Hey, FlinzoBot is me :3. To start a joint adventure, just use the command /start!"

    if any(word in text for word in ["you", "bot", "flinzo"]):
        return "Yes, I'm FlinzoBot!"

    if any(word in text for word in ["help", "support", "channel", "bug", "issue", "error"]):
        return "If you need help, please use the /help command first. If you don't find the answer to your question there, please see our support channel: https://t.me/FlinzoSupport"

    return "I don't understand what you mean. Please use the command /help to see all my commands or ping me!"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    if message_type == "group":
        if "@FlinzoBot" in text:
            new_text = text.replace("@FlinzoBot", "").strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)

    await update.message.reply_text(response)
