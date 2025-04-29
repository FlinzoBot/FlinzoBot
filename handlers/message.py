from telegram import Update
from telegram.ext import ContextTypes

def handle_response(text: str) -> str:
    if ["hi", "hello", "hey"] in text:
        return "Hello! Nice to see you. I'm FlinzoBot. To start our adventure use the command /start!"
    if ["github", "source", "repo"] in text:
        return "Hi user,my source code is open and available to everyone. You can check it out on github:\nhttps://github.com/FlinzoBot"
    if ["@FlinzoBot", "FlinzoBot"] in text:
        return "Hey, FlinzoBot is me :3. To start a joint adventure, just use the command /start!"
    if ["you", "bot", "flinzo"] in text:
        return "Yes, I'm FlinzoBot!"
    else:
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
