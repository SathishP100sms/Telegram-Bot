import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GMINI_API_KEY = os.getenv("GMINI_API_KEY")

genai.configure(api_key=GMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

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
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    prompt = f"{SYSTEM_PROMPT}\nUser: {user_text}\nAssistant:"
    response = model.generate_content(prompt)
    reply = response.text

    await update.message.reply_text(reply)

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)

    await telegram_app.initialize()
    await telegram_app.process_update(update)

    return {"status": "ok"}
