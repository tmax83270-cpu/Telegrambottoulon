from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import json
import os
from datetime import datetime

# =========================
# CONFIG
# =========================

TOKEN = "8864212024:AAG-6cttyivxxIcRTh4g9djZ3upJ6hgdcdY"
ADMIN_ID = 7047054214
USERS_FILE = "users.json"

# =========================
# INIT BOT
# =========================

app_bot = ApplicationBuilder().token(TOKEN).build()

# =========================
# USERS SYSTEM
# =========================

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_user(user_id):
    users = load_users()
    today = datetime.now().strftime("%Y-%m-%d")

    for u in users:
        if u["id"] == user_id:
            return

    users.append({
        "id": user_id,
        "date": today
    })

    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# =========================
# START (TON DESIGN ORIGINAL)
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id
    save_user(chat_id)

    texte = """BIENVENUE SUR PANAME DELIVERY 🗼✨
(Anciennement White Coffee 75)

🔹 Zone : Paris & Île De France 
🔹 Horaires : 14h/02h – 7j/7
🔹 Paiement : Cash uniquement
🔹 Livraison & Meet-up : Rapide et discret

CLIQUE SUR LA MINI APP POUR AVOIR ACCES AU MENU, INFOS, PROMO ETC  👇👇

/start pour redemarrer le bot 🤖"""

    image_url = "https://raw.githubusercontent.com/tmax83270-cpu/telegram-bot-railway/main/panamedelivery.jpg"

    keyboard = [
        [
            InlineKeyboardButton("🥔 Canal Potato", url="https://ptdym150.org/joinchat/KvW1uaqXsqcevh_qI-BH8Q"),
            InlineKeyboardButton("📢 Telegram", url="https://t.me/+GKfz6FwT-hg5NGJk")
        ],
        [
            InlineKeyboardButton("🛒 Mini-App", web_app=WebAppInfo(url="https://parfumwhite2.vercel.app/"))
        ]
        
    ]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=texte,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# ADMIN PANEL
# =========================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != ADMIN_ID:
        return

    keyboard = [
        [
            InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Users", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔄 Refresh", callback_data="admin_refresh")
        ]
    ]

    await update.message.reply_text(
        "🎛️ ADMIN DASHBOARD",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# CALLBACK FUNCTIONS FIXED
# =========================

async def send_stats(query, context):

    users = load_users()

    stats = {}

    for u in users:
        date = u.get("date", "inconnu")
        stats[date] = stats.get(date, 0) + 1

    text = "📊 STATS\n\n"

    for date, count in sorted(stats.items()):
        text += f"📅 {date} → {count}\n"

    text += f"\nTOTAL : {len(users)}"

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text
    )

async def send_users(query, context):

    users = load_users()

    text = "👥 USERS\n\n"

    for u in users:
        try:
            chat = await context.bot.get_chat(u["id"])

            name = chat.first_name or "?"
            username = f"@{chat.username}" if chat.username else "no username"

            text += f"🆔 {u['id']} | {name} | {username}\n"

        except:
            text += f"🆔 {u['id']} | inaccessible\n"

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text
    )

# =========================
# CALLBACK ROUTER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    data = query.data

    await query.answer()

    # USER SIDE
    if data == "info":

        image_info = "https://raw.githubusercontent.com/tmax83270-cpu/telegram-bot-railway/main/info.jpg"

        texte_info = """ℹ️ INFORMATIONS ℹ️

Tout est indiqué 👆
On vous livre même si vous êtes dans le fond du 77 ou le fond du 78 ✌️"""

        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image_info,
            caption=texte_info
        )

    elif data == "contact":

        image_contact = "https://raw.githubusercontent.com/tmax83270-cpu/telegram-bot-railway/main/contact.jpg"

        texte_contact = """✉️ CONTACT ✉️

📞 🔵 Telegram : @PanameDelivery

📞 🟢 WhatsApp : +33758594530"""

        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image_contact,
            caption=texte_contact
        )

    # ADMIN FIXED
    elif data == "admin_stats":
        await send_stats(query, context)

    elif data == "admin_users":
        await send_users(query, context)

    elif data == "admin_broadcast":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Utilise /broadcast message"
        )

    elif data == "admin_refresh":
        await admin_panel(update, context)

# =========================
# BROADCAST
# =========================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Utilisation : /broadcast message")
        return

    message = " ".join(context.args)

    users = load_users()

    sent = 0

    for u in users:
        try:
            await context.bot.send_message(chat_id=u["id"], text=message)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"Envoyé à {sent} users")

# =========================
# HANDLERS
# =========================

app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("admin", admin_panel))
app_bot.add_handler(CommandHandler("broadcast", broadcast))
app_bot.add_handler(CallbackQueryHandler(button_handler))

# =========================
# RUN
# =========================

print("Bot en ligne...")
app_bot.run_polling()
