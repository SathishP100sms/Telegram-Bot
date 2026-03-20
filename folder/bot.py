import os
import logging
import nest_asyncio
import google.generativeai as genai

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Fix async loop issue (important for some environments)
nest_asyncio.apply()

# Logging (VERY IMPORTANT for Render debugging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ==============================
# SYSTEM PROMPT
# ==============================
SYSTEM_PROMPT = """
You are a friendly, intelligent AI assistant chatting on Telegram.

Personality & behavior:
- Be natural, helpful, and confident
- Sound human, not robotic
- Do NOT mention Google, Gemini, or training sources
- Do NOT say "as a large language model"
- Answer clearly and concisely
- Use examples when helpful
- For coding questions, provide clean and correct code
- For math, show steps simply
- If the user greets, greet back casually

Identity rules:
- You are an AI assistant similar to ChatGPT
- You can acknowledge ChatGPT as another AI if asked
- Never say you are trained by Google

Safety:
- If you don’t know something, say so honestly
- Don’t hallucinate facts
"""

# ==============================
# ENV VARIABLES
# ==============================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================
# GEMINI SETUP
# ==============================
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ==============================
# HANDLERS
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm your AI assistant.\nAsk me anything!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    prompt = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"

    try:
        response = model.generate_content(prompt)

        # Safety: handle empty response
        reply = response.text if response.text else "⚠️ No response generated."

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(
            "⚠️ Something went wrong. Please try again later."
        )


# ==============================
# MAIN FUNCTION
# ==============================
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN not set")

    print("🚀 Bot is starting...")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN.strip()).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
