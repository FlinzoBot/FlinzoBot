from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',  'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--', 'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-','R': '.-.', 'S': '...',  'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--','Z': '--..',
    '0': '-----', '1': '.----', '2': '..---',
    '3': '...--','4': '....-', '5': '.....',
    '6': '-....','7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..',
    "'": '.----.','!': '-.-.--', '/': '-..-.',
    '(': '-.--.', ')': '-.--.-', '&': '.-...',
    ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-',
    '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
    ' ': '/'
}

REVERSE_MORSE_CODE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

ASK_MORSE_TEXT = 1

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(char.upper(), '') for char in text)

def morse_to_text(morse):
    words = morse.strip().split(' / ')
    decoded = []
    for word in words:
        letters = word.split()
        decoded.append(''.join(REVERSE_MORSE_CODE_DICT.get(l, '') for l in letters))
    return ' '.join(decoded)

async def morse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args or args[0].lower() not in ["encode", "decode"]:
        await update.message.reply_text(
            "Usage: /morse encode or /morse decode\n\n"
            "- `encode`: Convert text to Morse code\n"
            "- `decode`: Convert Morse code to text\n\n"
            "Example: /morse encode"
        )
        return ConversationHandler.END

    mode = args[0].lower()
    context.user_data["morse_mode"] = mode

    prompt = "Enter the text to encode:" if mode == "encode" else "Enter Morse code to decode (use `/` for spaces):"
    await update.message.reply_text(prompt, reply_markup=ReplyKeyboardRemove())
    return ASK_MORSE_TEXT

async def handle_morse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mode = context.user_data.get("morse_mode")

    if mode == "encode":
        result = text_to_morse(text)
    else:
        result = morse_to_text(text)

    await update.message.reply_text(f"The result is:\n{result}")
    return ConversationHandler.END

morse_conversation = ConversationHandler(
    entry_points=[CommandHandler("morse", morse_command)],
    states={
        ASK_MORSE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_morse)],
    },
    fallbacks=[],
)
