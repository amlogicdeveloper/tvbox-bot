import re
import logging
from collections import defaultdict
from time import time
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

message_history = defaultdict(lambda: defaultdict(list))
warn_count = defaultdict(lambda: defaultdict(int))


def get_mention(user):
    if user.username:
        return f"@{user.username}"
    return f"[{user.first_name}](tg://user?id={user.id})"


def contains_banned_word(text):
    text_lower = text.lower()
    for word in config.BANNED_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            return True, word
    return False, ""


def contains_suspicious_links(text):
    links = re.findall(r"(https?://\S+|t\.me/\S+|wa\.me/\S+)", text, re.IGNORECASE)
    if len(links) > config.MAX_LINKS_PER_MESSAGE:
        for link in links:
            if not any(allowed.lower() in link.lower() for allowed in config.ALLOWED_DOMAINS):
                return True, f"terlalu banyak link ({len(links)})"
    return False, ""


def is_flooding(chat_id, user_id, text):
    now = time()
    history = message_history[chat_id][user_id]
    message_history[chat_id][user_id] = [(t, msg) for t, msg in history if now - t < 60]
    history = message_history[chat_id][user_id]
    same_count = sum(1 for t, msg in history if msg == text)
    history.append((now, text))
    return same_count >= config.MAX_SAME_MESSAGE_PER_MINUTE


async def is_admin(update, user_id):
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def welcome_new_member(update, context):
    if not update.message or not update.message.new_chat_members:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        mention = get_mention(member)
        text = config.WELCOME_MESSAGE.format(
            brand=config.BRAND_NAME,
            tagline=config.BRAND_TAGLINE,
            mention=mention
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )


async def anti_spam(update, context):
    message = update.message
    if not message or not message.text:
        return
    user = message.from_user
    chat = message.chat
    if await is_admin(update, user.id):
        return
    if message.text.startswith("/"):
        return
    text = message.text
    reason = None

    banned, word = contains_banned_word(text)
    if banned:
        reason = f"kata terlarang: *{word}*"

    if not reason:
        has_link, link_reason = contains_suspicious_links(text)
        if has_link:
            reason = link_reason

    if not reason and is_flooding(chat.id, user.id, text):
        reason = "flooding (pesan berulang)"

    if not reason:
        return

    try:
        await message.delete()
        warn_count[chat.id][user.id] += 1
        warns = warn_count[chat.id][user.id]

        if warns >= config.WARN_LIMIT:
            await context.bot.ban_chat_member(chat.id, user.id)
            action = f"🔨 *BANNED* (warn {warns}/{config.WARN_LIMIT})"
        else:
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=datetime.now() + timedelta(seconds=config.MUTE_DURATION_SECONDS)
            )
            action = f"🔇 Muted {config.MUTE_DURATION_SECONDS//60} menit (warn {warns}/{config.WARN_LIMIT})"

        mention = get_mention(user)
        notif = (
            f"🚫 *Pesan dihapus!*\n\n"
            f"👤 User: {mention}\n"
            f"📝 Alasan: {reason}\n"
            f"⚡ Aksi: {action}"
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=notif,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Gagal proses spam: {e}")


async def cmd_start(update, context):
    await update.message.reply_text(
        f"👋 Halo! Saya bot resmi *{config.BRAND_NAME}*.\n\nGunakan /rules untuk melihat aturan grup.",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_rules(update, context):
    await update.message.reply_text(
        config.RULES_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )


async def cmd_help(update, context):
    help_text = (
        "🤖 *Bantuan Bot*\n\n"
        "/start - Mulai bot\n"
        "/rules - Lihat aturan grup\n"
        "/warn - Cek jumlah warn kamu\n"
        "/help - Bantuan ini\n\n"
        "*Khusus Admin:*\n"
        "/resetwarn - Reset warn user (reply ke pesan user)\n"
        "/unmute - Unmute user (reply ke pesan user)"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def cmd_warn(update, context):
    user = update.message.from_user
    warns = warn_count[update.effective_chat.id][user.id]
    await update.message.reply_text(
        f"⚠️ Kamu punya *{warns}/{config.WARN_LIMIT}* warning.",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_resetwarn(update, context):
    if not await is_admin(update, update.message.from_user.id):
        await update.message.reply_text("❌ Khusus admin.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply ke pesan user yang mau direset warn-nya.")
        return
    target = update.message.reply_to_message.from_user
    warn_count[update.effective_chat.id][target.id] = 0
    await update.message.reply_text(
        f"✅ Warn {get_mention(target)} sudah direset.",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_unmute(update, context):
    if not await is_admin(update, update.message.from_user.id):
        await update.message.reply_text("❌ Khusus admin.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply ke pesan user yang mau di-unmute.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(
            f"✅ {get_mention(target)} sudah di-unmute.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"Gagal unmute: {e}")


def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("warn", cmd_warn))
    app.add_handler(CommandHandler("resetwarn", cmd_resetwarn))
    app.add_handler(CommandHandler("unmute", cmd_unmute))
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, anti_spam
    ))
    logger.info("🤖 Bot Komunitas TvBox Android berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
