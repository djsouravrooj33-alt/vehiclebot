import os
import time
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

OWNER_NAME = "@amane_loyal_me"
CHANNEL_USERNAME = "@amane_friends"  # <-- change this
VEHICLE_API = "https://amane.djsouravrooj33.workers.dev/?rc="
USERS_FILE = "authorized_users.txt"

last_used = {}

# ===== USERS STORAGE =====
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(int(x.strip()) for x in f if x.strip().isdigit())

def save_all(users):
    with open(USERS_FILE, "w") as f:
        for u in users:
            f.write(str(u) + "\n")

AUTHORIZED_USERS = load_users()

# ===== CHECKS =====
def is_owner(update: Update):
    return update.effective_user.id == OWNER_ID

def is_authorized(update: Update):
    return update.effective_user.id in AUTHORIZED_USERS or is_owner(update)

def anti_spam(user_id):
    now = time.time()
    last = last_used.get(user_id, 0)
    last_used[user_id] = now
    return now - last < 3

async def is_user_joined(update, context):
    try:
        m = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=update.effective_user.id
        )
        return m.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

def join_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]
    ])

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 You are not authorized.")
        return

    if not await is_user_joined(update, context):
        await update.message.reply_text(
            "🔒 Join channel to use this bot",
            reply_markup=join_btn()
        )
        return

    await update.message.reply_text(
        f"✅ Vehicle Bot Active\n"
        f"👑 Owner: {OWNER_NAME}\n\n"
        f"🚗 Send RC number"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if not await is_user_joined(update, context):
        await update.message.reply_text(
            "🔒 Join channel first",
            reply_markup=join_btn()
        )
        return

    await update.message.reply_text(
        "🤖 Vehicle Bot Help\n\n"
        "Commands:\n"
        "/start – Start bot\n"
        "/help – Help menu\n"
        "/adduser – Owner only\n"
        "/removeuser – Owner only\n"
        "/listusers – Owner only\n\n"
        f"👑 Owner: {OWNER_NAME}"
    )

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /adduser <user_id>")
        return

    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid ID")
        return

    if uid in AUTHORIZED_USERS:
        await update.message.reply_text("ℹ️ Already authorized")
        return

    AUTHORIZED_USERS.add(uid)
    save_all(AUTHORIZED_USERS)
    await update.message.reply_text(f"✅ Authorized: {uid}")

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("Usage: /removeuser <user_id>")
        return

    AUTHORIZED_USERS.discard(uid)
    save_all(AUTHORIZED_USERS)
    await update.message.reply_text(f"❌ Removed: {uid}")

async def listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not AUTHORIZED_USERS:
        await update.message.reply_text("No authorized users")
        return

    text = "👥 Authorized Users:\n\n"
    for u in AUTHORIZED_USERS:
        text += f"• {u}\n"

    await update.message.reply_text(text)

# ===== SEARCH =====
async def vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if not await is_user_joined(update, context):
        await update.message.reply_text(
            "🔒 Join channel to search",
            reply_markup=join_btn()
        )
        return

    if anti_spam(update.effective_user.id):
        await update.message.reply_text("⚠️ Slow down")
        return

    rc = update.message.text.strip()
    if len(rc) < 5:
        await update.message.reply_text("❌ Invalid RC")
        return

    try:
        r = requests.get(VEHICLE_API + rc, timeout=10)
        await update.message.reply_text(
            f"🚗 Vehicle Info\n\n"
            f"{r.text}\n\n"
            f"🔎 By: {OWNER_NAME}"
        )
    except:
        await update.message.reply_text("⚠️ API Error")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("listusers", listusers))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, vehicle))
    print("🔥 Ultimate Secure Bot Running")
    app.run_polling()

if __name__ == "__main__":
    main()
