from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import json
import os
from datetime import datetime

=========================

CONFIG

=========================

⚠️ Utilise un NOUVEAU token après avoir révoqué l’ancien

TOKEN = os.getenv(“8864212024:AAFK82p_HitGX2izvONNQKKSM10Mmhs4Ihc”)

ADMIN_ID = 8923109411
USERS_FILE = “users.json”

if not TOKEN:
raise ValueError(“BOT_TOKEN est introuvable dans les variables d’environnement”)

=========================

INIT BOT

=========================

app_bot = ApplicationBuilder().token(TOKEN).build()

=========================

USERS SYSTEM

=========================

def load_users():

if not os.path.exists(USERS_FILE):
    return []
try:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
        if isinstance(users, list):
            return users
        return []
except Exception as e:
    print(f"Erreur load_users : {e}")
    return []

def save_user(user_id):

users = load_users()
today = datetime.now().strftime("%Y-%m-%d")
for user in users:
    if user.get("id") == user_id:
        return
users.append({
    "id": user_id,
    "date": today
})
try:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"Erreur save_user : {e}")

=========================

ADMIN KEYBOARD

=========================

def admin_keyboard():

return InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "📊 Stats",
            callback_data="admin_stats"
        ),
        InlineKeyboardButton(
            "👥 Users",
            callback_data="admin_users"
        )
    ],
    [
        InlineKeyboardButton(
            "📣 Broadcast",
            callback_data="admin_broadcast"
        ),
        InlineKeyboardButton(
            "🔄 Refresh",
            callback_data="admin_refresh"
        )
    ]
])

=========================

START

=========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

chat_id = update.effective_chat.id
save_user(chat_id)
texte = """BIENVENUE SUR PARFUM TOULON ✨

🔹 Zone : Paris & Île De France
🔹 Horaires : 8h-20h – 7j/7
🔹 Paiement : Carte, Virement ou Cash
🔹 Livraison & Meet-up : Rapide

CLIQUE SUR LA MINI APP POUR AVOIR ACCES AUX PRODUITS, INFOS ET PROMOTIONS 👇👇

/start pour redémarrer le bot 🤖”””

image_url = (
    "https://raw.githubusercontent.com/"
    "tmax83270-cpu/"
    "telegram-bot-railway/"
    "main/panamedelivery.jpg"
)
keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "📞 Contact 1",
            url="https://example.com"
        ),
        InlineKeyboardButton(
            "📞 Contact 2",
            url="https://example.org"
        )
    ],
    [
        InlineKeyboardButton(
            "🛒 Mini-App",
            web_app=WebAppInfo(
                url="https://parfumwhite2.vercel.app/"
            )
        )
    ]
])
try:
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=texte,
        reply_markup=keyboard
    )
except Exception as e:
    print(f"Erreur photo : {e}")
    await context.bot.send_message(
        chat_id=chat_id,
        text=texte,
        reply_markup=keyboard
    )

=========================

ADMIN PANEL

=========================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.id != ADMIN_ID:
    return
await update.effective_message.reply_text(
    "🎛️ ADMIN DASHBOARD",
    reply_markup=admin_keyboard()
)

=========================

ADMIN STATS

=========================

async def send_stats(query):

users = load_users()
stats = {}
for user in users:
    date = user.get("date", "inconnu")
    stats[date] = stats.get(date, 0) + 1
text = "📊 STATS\n\n"
if stats:
    for date, count in sorted(stats.items()):
        text += f"📅 {date} → {count}\n"
else:
    text += "Aucun utilisateur.\n"
text += f"\n👥 TOTAL : {len(users)}"
await query.message.reply_text(text)

=========================

ADMIN USERS

=========================

async def send_users(query, context):

users = load_users()
if not users:
    await query.message.reply_text(
        "👥 Aucun utilisateur enregistré."
    )
    return
text = "👥 USERS\n\n"
for user in users:
    user_id = user.get("id")
    try:
        chat = await context.bot.get_chat(user_id)
        name = chat.first_name or "?"
        username = (
            f"@{chat.username}"
            if chat.username
            else "Sans username"
        )
        line = f"🆔 {user_id} | {name} | {username}\n"
    except Exception as e:
        print(f"Erreur utilisateur {user_id} : {e}")
        line = f"🆔 {user_id} | inaccessible\n"
    # Limite Telegram
    if len(text + line) > 3500:
        await query.message.reply_text(text)
        text = "👥 USERS (suite)\n\n"
    text += line
await query.message.reply_text(text)

=========================

CALLBACK ROUTER

=========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

query = update.callback_query
if not query:
    return
await query.answer()
data = query.data
# =========================
# ADMIN SECURITY
# =========================
if data.startswith("admin_"):
    if query.message.chat_id != ADMIN_ID:
        await query.answer(
            "Accès refusé.",
            show_alert=True
        )
        return
# =========================
# ADMIN STATS
# =========================
if data == "admin_stats":
    await send_stats(query)
# =========================
# ADMIN USERS
# =========================
elif data == "admin_users":
    await send_users(query, context)
# =========================
# ADMIN BROADCAST
# =========================
elif data == "admin_broadcast":
    await query.message.reply_text(
        "📣 Utilise :\n\n/broadcast ton message"
    )
# =========================
# ADMIN REFRESH
# =========================
elif data == "admin_refresh":
    await query.message.edit_text(
        "🎛️ ADMIN DASHBOARD",
        reply_markup=admin_keyboard()
    )

=========================

BROADCAST

=========================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.id != ADMIN_ID:
    return
if not context.args:
    await update.message.reply_text(
        "Utilisation : /broadcast ton message"
    )
    return
message = " ".join(context.args)
users = load_users()
sent = 0
failed = 0
for user in users:
    user_id = user.get("id")
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message
        )
        sent += 1
    except Exception as e:
        print(
            f"Erreur broadcast {user_id} : {e}"
        )
        failed += 1
await update.message.reply_text(
    f"📣 Broadcast terminé\n\n"
    f"✅ Envoyé : {sent}\n"
    f"❌ Échecs : {failed}"
)

=========================

ERROR HANDLER

=========================

async def error_handler(update, context):

print("❌ ERREUR BOT :")
print(context.error)

=========================

HANDLERS

=========================

app_bot.add_handler(
CommandHandler(“start”, start)
)

app_bot.add_handler(
CommandHandler(“admin”, admin_panel)
)

app_bot.add_handler(
CommandHandler(“broadcast”, broadcast)
)

app_bot.add_handler(
CallbackQueryHandler(button_handler)
)

app_bot.add_error_handler(error_handler)

=========================

RUN

=========================

print(“🤖 Bot en ligne…”)

app_bot.run_polling()
