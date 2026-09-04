from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import json
import os
from datetime import datetime


# =========================
# CONFIG
# =========================

TOKEN = os.getenv("8864212024:AAFK82p_HitGX2izvONNQKKSM10Mmhs4Ihc")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7047054214"))
USERS_FILE = "users.json"

if not TOKEN:
    raise ValueError(
        "BOT_TOKEN est introuvable. "
        "Ajoute BOT_TOKEN dans les variables d'environnement Railway."
    )


# =========================
# INIT BOT
# =========================

app_bot = ApplicationBuilder().token(TOKEN).build()


# =========================
# USERS SYSTEM
# =========================

def load_users():
    """Charge les utilisateurs enregistrés."""

    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, list):
                return data

            return []

    except Exception as e:
        print(f"Erreur load_users: {e}")
        return []


def save_users(users):
    """Sauvegarde les utilisateurs."""

    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                users,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        print(f"Erreur save_users: {e}")


def save_user(user_id):
    """Ajoute un utilisateur s'il n'existe pas déjà."""

    users = load_users()
    today = datetime.now().strftime("%Y-%m-%d")

    for user in users:
        if user.get("id") == user_id:
            return

    users.append({
        "id": user_id,
        "date": today
    })

    save_users(users)

    print(f"Nouvel utilisateur enregistré: {user_id}")


# =========================
# ADMIN KEYBOARD
# =========================

def get_admin_keyboard():

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
            ),
            InlineKeyboardButton(
                "🔄 Refresh",
                callback_data="admin_refresh"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    save_user(chat_id)

    texte = """BIENVENUE SUR PANAME DELIVERY 🗼✨
(Anciennement White Coffee 75)

🔹 Zone : Paris & Île De France
🔹 Horaires : 14h/02h – 7j/7
🔹 Paiement : par carte
🔹 Livraison & Meet-up : Rapide

CLIQUE SUR LA MINI APP POUR AVOIR ACCES AU PARFUM, INFOS, PROMO ETC 👇👇

/start pour redemarrer le bot 🤖"""

    image_url = (
        "https://raw.githubusercontent.com/"
        "tmax83270-cpu/telegram-bot-railway/"
        "main/panamedelivery.jpg"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🥔 Canal",
                url="https://ptdym150.org/joinchat/KvW1uaqXsqcevh_qI-BH8Q"
            ),
            InlineKeyboardButton(
                "📢 Site",
                url="https://t.me/+GKfz6FwT-hg5NGJk"
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
    ]

    try:

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=texte,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:

        print(f"Erreur START photo: {e}")

        # Si l'image ne fonctionne pas,
        # le bot envoie quand même le message

        await context.bot.send_message(
            chat_id=chat_id,
            text=texte,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# =========================
# ADMIN PANEL
# =========================

async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat.id != ADMIN_ID:
        return

    markup = get_admin_keyboard()

    await update.effective_message.reply_text(
        "🎛️ ADMIN DASHBOARD",
        reply_markup=markup
    )


# =========================
# ADMIN STATS
# =========================

async def send_stats(query, context):

    users = load_users()

    stats = {}

    for user in users:

        date = user.get("date", "inconnu")

        stats[date] = stats.get(date, 0) + 1

    text = "📊 STATS\n\n"

    if not stats:

        text += "Aucun utilisateur enregistré."

    else:

        for date, count in sorted(stats.items()):

            text += f"📅 {date} → {count}\n"

    text += f"\n👥 TOTAL : {len(users)}"

    await query.message.reply_text(text)


# =========================
# ADMIN USERS
# =========================

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
                else "no username"
            )

            line = (
                f"🆔 {user_id} | "
                f"{name} | "
                f"{username}\n"
            )

        except Exception as e:

            print(
                f"Erreur utilisateur {user_id}: {e}"
            )

            line = (
                f"🆔 {user_id} | inaccessible\n"
            )

        # Évite la limite Telegram de 4096 caractères

        if len(text + line) > 3800:

            await query.message.reply_text(text)

            text = "👥 USERS (suite)\n\n"

        text += line

    if text:

        await query.message.reply_text(text)


# =========================
# CALLBACK ROUTER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    data = query.data

    await query.answer()

    # =========================
    # USER INFO
    # =========================

    if data == "info":

        image_info = (
            "https://raw.githubusercontent.com/"
            "tmax83270-cpu/telegram-bot-railway/"
            "main/info.jpg"
        )

        texte_info = """ℹ️ INFORMATIONS ℹ️

Tout est indiqué 👆
On vous livre même si vous êtes dans le fond du 77 ou le fond du 78 ✌️"""

        try:

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=image_info,
                caption=texte_info
            )

        except Exception as e:

            print(f"Erreur INFO: {e}")

            await query.message.reply_text(
                texte_info
            )


    # =========================
    # USER CONTACT
    # =========================

    elif data == "contact":

        image_contact = (
            "https://raw.githubusercontent.com/"
            "tmax83270-cpu/telegram-bot-railway/"
            "main/contact.jpg"
        )

        texte_contact = """✉️ CONTACT ✉️

📞 🔵 Telegram : @PanameDelivery

📞 🟢 WhatsApp : +33758594530"""

        try:

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=image_contact,
                caption=texte_contact
            )

        except Exception as e:

            print(f"Erreur CONTACT: {e}")

            await query.message.reply_text(
                texte_contact
            )


    # =========================
    # ADMIN SECURITY
    # =========================

    elif data.startswith("admin_"):

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

            await send_stats(
                query,
                context
            )


        # =========================
        # ADMIN USERS
        # =========================

        elif data == "admin_users":

            await send_users(
                query,
                context
            )


        # =========================
        # ADMIN BROADCAST
        # =========================

        elif data == "admin_broadcast":

            await query.message.reply_text(
                "📣 Pour envoyer un message :\n\n"
                "/broadcast ton message"
            )


        # =========================
        # ADMIN REFRESH
        # =========================

        elif data == "admin_refresh":

            await query.message.edit_text(
                "🎛️ ADMIN DASHBOARD",
                reply_markup=get_admin_keyboard()
            )


# =========================
# BROADCAST
# =========================

async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat.id != ADMIN_ID:
        return

    if not context.args:

        await update.message.reply_text(
            "❌ Utilisation :\n"
            "/broadcast ton message"
        )

        return

    message = " ".join(context.args)

    users = load_users()

    sent = 0
    failed = 0

    await update.message.reply_text(
        f"📣 Envoi du broadcast à {len(users)} utilisateurs..."
    )

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
                f"Erreur broadcast {user_id}: {e}"
            )

            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast terminé\n\n"
        f"📨 Envoyé : {sent}\n"
        f"❌ Erreurs : {failed}"
    )


# =========================
# ERROR HANDLER
# =========================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print("ERREUR BOT :")

    print(context.error)


# =========================
# HANDLERS
# =========================

app_bot.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app_bot.add_handler(
    CommandHandler(
        "admin",
        admin_panel
    )
)

app_bot.add_handler(
    CommandHandler(
        "broadcast",
        broadcast
    )
)

app_bot.add_handler(
    CallbackQueryHandler(
        button_handler
    )
)

app_bot.add_error_handler(
    error_handler
)


# =========================
# RUN
# =========================

print("🤖 Bot en ligne...")

app_bot.run_polling()
