import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import google.generativeai as genai

# ENV VARIABLES
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# FastAPI app
app = FastAPI()

# Telegram app
telegram_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Ask me anything.")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    prompt = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"

    try:
        response = model.generate_content(prompt)
        reply = response.text
    except Exception:
        reply = "⚠️ AI error."

    await update.message.reply_text(reply)

# Add handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# Webhook route
@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


# Set webhook automatically
@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")
    await telegram_app.bot.set_webhook(url=webhook_url)
