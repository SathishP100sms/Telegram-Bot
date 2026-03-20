from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
import google.generativeai as genai

# -------------------- FASTAPI --------------------
app = FastAPI()

# -------------------- ENV VARIABLES --------------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # ✅ FIXED TYPO

# -------------------- GEMINI SETUP --------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------- TELEGRAM APP --------------------
telegram_app = ApplicationBuilder().token(TOKEN).build()

# -------------------- SYSTEM PROMPT --------------------
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

# -------------------- COMMAND HANDLER --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your AI bot 🤖")

# -------------------- MESSAGE HANDLER --------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_msg = update.message.text

        prompt = f"{SYSTEM_PROMPT}\nUser: {user_msg}\nAssistant:"
        response = model.generate_content(prompt)

        reply = response.text if response.text else "Sorry, I couldn't generate a response."

        await update.message.reply_text(reply)

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("⚠️ Something went wrong. Try again later.")

# -------------------- REGISTER HANDLERS --------------------
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

# -------------------- STARTUP EVENT --------------------
@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()
    print("✅ Telegram bot started")

# -------------------- SHUTDOWN EVENT --------------------
@app.on_event("shutdown")
async def shutdown():
    await telegram_app.stop()
    print("🛑 Telegram bot stopped")

# -------------------- ROOT (OPTIONAL) --------------------
@app.get("/")
async def root():
    return {"message": "Bot is running 🚀"}

# -------------------- WEBHOOK --------------------
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)

        await telegram_app.process_update(update)

        return {"ok": True}

    except Exception as e:
        print("Webhook Error:", e)
        return {"ok": False}
