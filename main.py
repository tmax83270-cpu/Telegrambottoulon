from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import json
import os
from datetime import datetime

=========================

CONFIG

=========================

TOKEN = "8864212024:AAG-6cttyivxxIcRTh4g9djZ3upJ6hgdcdY"

ADMIN_ID = 8923109411

USERS_FILE = "users.json"

=========================

INIT BOT

=========================

app = ApplicationBuilder().token(TOKEN).build()

=========================

USERS SYSTEM

=========================

def load_users():

if not os.path.exists(USERS_FILE):
    return []
try:
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
except Exception as e:
    print("Erreur chargement users :", e)
    return []

def save_user(user_id):

users = load_users()
# Vérifie si l'utilisateur existe déjà
for user in users:
    if user.get("id") == user_id:
        return
users.append({
    "id": user_id,
    "date": datetime.now().strftime("%Y-%m-%d")
})
try:
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            users,
            file,
            ensure_ascii=False,
            indent=2
        )
    print("Nouvel utilisateur :", user_id)
except Exception as e:
    print("Erreur sauvegarde :", e)

=========================

START

=========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

chat_id = update.effective_chat.id
# Enregistre l'utilisateur
save_user(chat_id)
texte = """BIENVENUE SUR PARFUM TOULON ✨

🔹 Zone : Toulon & alentours
🔹 Horaires : 8h - 20h
🔹 Paiement : Carte, virement ou espèces
🔹 Livraison & Meet-up : Rapide

👇 CLIQUE SUR LA MINI-APP POUR VOIR LES PRODUITS, INFOS ET PROMOTIONS 👇”””

# Ton image
image_url = (
    "https://raw.githubusercontent.com/"
    "tmax83270-cpu/telegram-bot-railway/"
    "main/panamedelivery.jpg"
)
# BOUTONS
keyboard = [
    [
        InlineKeyboardButton(
            "📞 Contact",
            callback_data="contact"
        ),
        InlineKeyboardButton(
            "ℹ️ Informations",
            callback_data="info"
        )
    ],
    [
        InlineKeyboardButton(
            "🛒 Ouvrir la Mini-App",
            web_app=WebAppInfo(
                url="https://parfumwhite2.vercel.app/"
            )
        )
    ]
]
try:
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=texte,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
except Exception as e:
    print("Erreur image :", e)
    # Envoie quand même le message
    await context.bot.send_message(
        chat_id=chat_id,
        text=texte,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

=========================

INFO

=========================

async def send_info(query, context):

texte = """ℹ️ INFORMATIONS

📍 Zone : Toulon & alentours

🕗 Horaires : 8h - 20h

💳 Paiement :
Carte • Virement • Espèces

🚗 Livraison & Meet-up rapide”””

await query.message.reply_text(texte)

=========================

CONTACT

=========================

async def send_contact(query, context):

texte = """📞 CONTACT

🔵 Telegram : @TonTelegram

🟢 WhatsApp : Ton numéro”””

await query.message.reply_text(texte)

=========================

ADMIN PANEL

=========================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.id != ADMIN_ID:
    return
keyboard = [
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
        )
    ]
]
await update.message.reply_text(
    "🎛️ ADMIN DASHBOARD",
    reply_markup=InlineKeyboardMarkup(keyboard)
)

=========================

STATS

=========================

async def send_stats(query):

users = load_users()
text = "📊 STATISTIQUES\n\n"
text += f"👥 Total utilisateurs : {len(users)}"
await query.message.reply_text(text)

=========================

USERS LIST

=========================

async def send_users(query):

users = load_users()
if not users:
    await query.message.reply_text(
        "Aucun utilisateur enregistré."
    )
    return
text = "👥 UTILISATEURS\n\n"
for user in users:
    text += f"🆔 {user.get('id')}\n"
    # Évite la limite Telegram
    if len(text) > 3500:
        await query.message.reply_text(text)
        text = "👥 SUITE\n\n"
if text:
    await query.message.reply_text(text)

=========================

CALLBACK BUTTONS

=========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

query = update.callback_query
await query.answer()
data = query.data
# =========================
# INFO
# =========================
if data == "info":
    await send_info(query, context)
# =========================
# CONTACT
# =========================
elif data == "contact":
    await send_contact(query, context)
# =========================
# ADMIN SECURITY
# =========================
elif data.startswith("admin_"):
    if query.message.chat_id != ADMIN_ID:
        await query.answer(
            "Accès refusé",
            show_alert=True
        )
        return
    # STATS
    if data == "admin_stats":
        await send_stats(query)
    # USERS
    elif data == "admin_users":
        await send_users(query)
    # BROADCAST
    elif data == "admin_broadcast":
        await query.message.reply_text(
            "📣 Utilise cette commande :\n\n"
            "/broadcast Ton message"
        )

=========================

BROADCAST

=========================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

# Sécurité admin
if update.effective_chat.id != ADMIN_ID:
    return
if not context.args:
    await update.message.reply_text(
        "Utilisation :\n"
        "/broadcast Ton message"
    )
    return
message = " ".join(context.args)
users = load_users()
sent = 0
failed = 0
for user in users:
    try:
        await context.bot.send_message(
            chat_id=user.get("id"),
            text=message
        )
        sent += 1
    except Exception as e:
        print("Erreur broadcast :", e)
        failed += 1
await update.message.reply_text(
    f"📣 BROADCAST TERMINÉ\n\n"
    f"✅ Envoyé : {sent}\n"
    f"❌ Erreurs : {failed}"
)

=========================

ERROR HANDLER

=========================

async def error_handler(update, context):

print("ERREUR :", context.error)

=========================

HANDLERS

=========================

app.add_handler(

CommandHandler(
    "start",
    start
)

)

app.add_handler(

CommandHandler(
    "admin",
    admin_panel
)

)

app.add_handler(

CommandHandler(
    "broadcast",
    broadcast
)

)

app.add_handler(

CallbackQueryHandler(
    button_handler
)

)

app.add_error_handler(
error_handler
)

=========================

START BOT

=========================

print(“🤖 Bot en ligne…”)

app.run_polling()
