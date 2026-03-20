from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import google.generativeai as genai

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

telegram_app = ApplicationBuilder().token(TOKEN).build()

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
    await update.message.reply_text("Hi! I'm your AI bot 🤖")


# Handle messages
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    prompt = f"{SYSTEM_PROMPT}\nUser: {user_msg}\nAssistant:"
    response = model.generate_content(prompt)
    await update.message.reply_text(response.text)


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))


# 🚀 WEBHOOK ENDPOINT 
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # process Telegram update
    await telegram_app.process_update(Update.de_json(data, telegram_app.bot))

    return {"ok": True}
