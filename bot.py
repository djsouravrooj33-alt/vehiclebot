import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_USERNAME = "@amane_friends"  # @ সহ
OWNER_NAME = "@amane_loyal_me"

authorized_users = set([OWNER_ID])

# ================= HELPERS =================
def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]
    ])

async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_joined(context.bot, user_id):
        await update.message.reply_text(
            "🚫 channel join ",
            reply_markup=join_keyboard()
        )
        return

    if user_id not in authorized_users:
        await update.message.reply_text("❌ তুমি authorized নও")
        return

    await update.message.reply_text(
        f"✅ Welcome!\n\nBot Owner: {OWNER_NAME}"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Bot start\n"
        "/help - Help menu\n"
        "/adduser <id> - Add authorized user (Owner only)"
    )

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can use this")
        return

    if not context.args:
        await update.message.reply_text("Usage: /adduser user_id")
        return

    try:
        uid = int(context.args[0])
        authorized_users.add(uid)
        await update.message.reply_text(f"✅ User {uid} authorized")
    except:
        await update.message.reply_text("❌ Invalid user id")

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("adduser", adduser))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
