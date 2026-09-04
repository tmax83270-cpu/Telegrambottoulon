import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv(“8864212024:AAG-6cttyivxxIcRTh4g9djZ3upJ6hgdcdY”)

if not TOKEN:
raise RuntimeError(“BOT_TOKEN est absent des variables Railway”)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“✅ Bot fonctionne !”)

async def error_handler(update, context):
print(“ERREUR :”, repr(context.error))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler(“start”, start))
app.add_error_handler(error_handler)

print(“🤖 Démarrage du bot…”)

app.run_polling()
