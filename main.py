import importlib
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from handlers.message import handle_message
from handlers.start import help_command, start_command
from logger import setup_logger

load_dotenv()

logger = setup_logger()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("Bot token is missing. Please set it in the .env file.")
    exit(1)

def load_handlers(app, package="handlers"):
    for filename in os.listdir(package):
        if filename.endswith(".py") and filename not in ("__init__.py", "start.py", "help.py", "message.py"):
            modulename = filename[:-3]  
            module = importlib.import_module(f"{package}.{modulename}") 

            for attr in dir(module):  
                if attr.endswith("_conversation") or attr.endswith("_handler"): 
                    handler = getattr(module, attr)
                    app.add_handler(handler)  
                    logger.info(f"Loaded handler: {attr} from {modulename}")


if __name__ == "__main__":
    logger.info("Starting FlinzoBot...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    load_handlers(app)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()