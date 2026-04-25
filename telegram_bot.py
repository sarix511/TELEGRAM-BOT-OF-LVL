import os
import asyncio
import json
import logging
import time
from html import escape as html_escape

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["8607292797:AAE_JgQFoLkT_eb3yrt5XFfdZ9grsxBK3_E"]
CHANNEL = os.environ["hayato_codex"]
CHANNEL_LINK = f"https://t.me/{CHANNEL.lstrip('@')}"

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BOT_DIR, "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

SESSIONS: dict[int, dict] = {}

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("hayato-bot")

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
PROGRESS = [
    "▰▱▱▱▱▱▱▱▱▱",
    "▰▰▱▱▱▱▱▱▱▱",
    "▰▰▰▱▱▱▱▱▱▱",
    "▰▰▰▰▱▱▱▱▱▱",
    "▰▰▰▰▰▱▱▱▱▱",
    "▰▰▰▰▰▰▱▱▱▱",
    "▰▰▰▰▰▰▰▱▱▱",
    "▰▰▰▰▰▰▰▰▱▱",
    "▰▰▰▰▰▰▰▰▰▱",
    "▰▰▰▰▰▰▰▰▰▰",
]

WELCOME = (
    "✨━━━━━━━━━━━━━━━━━━✨\n"
    "🌙  <b>𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨𝗔𝗟𝗔𝗜𝗞𝗨𝗠</b>  🌙\n"
    "✨━━━━━━━━━━━━━━━━━━✨\n\n"
    "🤖 <b>It's <u>HAYATO LEVEL UP BOT</u></b>\n"
    "🛡️ <b>100% SAFE</b>   ⚡ <b>VERSION 2.0</b>\n\n"
    "💎 <i>Premium • Stable • Lightning Fast</i>\n\n"
    "📢 <b>Join our official channel to continue</b> 👇"
)

NOT_JOINED = (
    "🚫━━━━━━━━━━━━━━━━━🚫\n"
    "💩  <b>𝗔𝗕𝗘 𝗢𝗬𝗘 𝗝𝗢𝗜𝗡 𝗞𝗔𝗥 𝗟𝗘</b>  💩\n"
    "🚫━━━━━━━━━━━━━━━━━🚫\n\n"
    "🗿 <b>JOIN NAI HUA</b> 🗿\n\n"
    f"👉 First join <b>{CHANNEL}</b>\n"
    "👉 Then come back and tap <b>Continue 🗿</b>"
)

WELCOME_AFTER = (
    "🎉━━━━━━━━━━━━━━━━━━🎉\n"
    "🚀  <b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢</b>  🚀\n"
    "🔥  <b>HAYATO LEVEL UP BOT V2.0</b>  🔥\n"
    "✅  <b>100% WORKING</b>  ✅\n"
    "🎉━━━━━━━━━━━━━━━━━━🎉\n\n"
    "🔐 <b>Please send your credentials to start</b>\n\n"
    "📌 <b>FORMAT</b>\n"
    "<code>UID:PASSWORD</code>\n\n"
    "📋 <b>Example</b>\n"
    "<code>4608211147:47F51CA1292B9E30C79A850757F95B73080737D18EFC3CDE4F483259B00FA7B7</code>\n\n"
    "🛑 Use /stop anytime to stop the bot."
)

INVALID_FORMAT = (
    "❌ <b>Invalid format!</b>\n\n"
    "Send your credentials as:\n"
    "<code>UID:PASSWORD</code>"
)


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 Join My Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("Continue 🗿", callback_data="continue")],
        ]
    )


async def is_member(ctx: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await ctx.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator", "owner")
    except Exception as e:
        log.warning("member check failed: %s", e)
        return False


async def play_loading(msg, label: str, total_steps: int = 10, delay: float = 0.18):
    for i in range(total_steps):
        try:
            await msg.edit_text(
                f"{SPINNER[i % len(SPINNER)]} <b>{label}</b>\n"
                f"<code>{PROGRESS[i]}</code>  {(i + 1) * 10}%",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
        await asyncio.sleep(delay)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = await ctx.bot.send_message(chat_id, "⚡ <b>Booting...</b>", parse_mode=ParseMode.HTML)
    await play_loading(msg, "Initializing Hayato Level Up Bot...")
    try:
        await msg.edit_text(WELCOME, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())
    except Exception:
        await ctx.bot.send_message(
            chat_id, WELCOME, parse_mode=ParseMode.HTML, reply_markup=main_keyboard()
        )


async def cb_continue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    check = await ctx.bot.send_message(chat_id, "🔎 <b>Verifying...</b>", parse_mode=ParseMode.HTML)
    await play_loading(check, "Checking your channel membership...", total_steps=6, delay=0.15)

    joined = await is_member(ctx, user_id)
    if not joined:
        try:
            await check.edit_text(
                NOT_JOINED, parse_mode=ParseMode.HTML, reply_markup=main_keyboard()
            )
        except Exception:
            await ctx.bot.send_message(
                chat_id, NOT_JOINED, parse_mode=ParseMode.HTML, reply_markup=main_keyboard()
            )
        return

    SESSIONS.setdefault(chat_id, {})["joined"] = True
    try:
        await check.edit_text(WELCOME_AFTER, parse_mode=ParseMode.HTML)
    except Exception:
        await ctx.bot.send_message(chat_id, WELCOME_AFTER, parse_mode=ParseMode.HTML)


async def safe_send(ctx, chat_id, text, **kw):
    try:
        return await ctx.bot.send_message(chat_id, text, **kw)
    except Exception as e:
        log.warning("send failed: %s", e)
        return None


def detect_status(line: str, state: dict) -> str | None:
    low = line.lower()
    if "bot online" in low or "🤖 bot" in line:
        state["status"] = "online"
        state["online_at"] = time.time()
        return (
            "✅━━━━━━━━━━━━━━━━━✅\n"
            "🟢  <b>BOT IS ONLINE!</b>  🟢\n"
            "✅━━━━━━━━━━━━━━━━━✅\n\n"
            "🚀 <b>Successfully logged in</b>\n"
            "📡 <b>Streaming live game logs below</b>\n\n"
            "🎮 In-game commands:\n"
            "<code>/lw &lt;team_code&gt;</code> – start auto level up\n"
            "<code>/stop_auto</code> – stop auto level up\n"
            "<code>/help</code> – show in-game help\n\n"
            "ℹ️ Type <b>/status</b> here for session info.\n"
            "🛑 Type <b>/stop</b> to stop the bot."
        )
    if "logging in with uid" in low:
        state["status"] = "logging_in"
        return "🔑 <b>Logging into Garena…</b>"
    if line.startswith("❌") or "error:" in low or "failed" in low or "traceback" in low:
        state["status"] = "error"
        state["last_error"] = line.strip()[:300]
        return None
    if "restarting due to error" in low:
        state["status"] = "restarting"
        return "🔄 <b>Restarting after error…</b>"
    return None


async def stream_subprocess(process: asyncio.subprocess.Process, ctx, chat_id: int, state: dict):
    buffer: list[str] = []
    last_sent = asyncio.get_event_loop().time()
    SEND_INTERVAL = 1.5
    MAX_CHARS = 3500

    async def flush():
        nonlocal buffer
        text = "".join(buffer).strip()
        buffer = []
        if not text:
            return
        if len(text) > MAX_CHARS:
            text = "...\n" + text[-MAX_CHARS:]
        await safe_send(
            ctx,
            chat_id,
            f"📡 <b>LIVE LOG</b>\n<pre>{html_escape(text)}</pre>",
            parse_mode=ParseMode.HTML,
        )

    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            try:
                decoded = line.decode("utf-8", errors="replace")
            except Exception:
                decoded = str(line)
            buffer.append(decoded)

            notice = detect_status(decoded, state)
            if notice:
                await flush()
                await safe_send(ctx, chat_id, notice, parse_mode=ParseMode.HTML)
                last_sent = asyncio.get_event_loop().time()
                continue

            now = asyncio.get_event_loop().time()
            if (now - last_sent) >= SEND_INTERVAL or sum(len(s) for s in buffer) >= MAX_CHARS:
                await flush()
                last_sent = now
    except asyncio.CancelledError:
        await flush()
        raise
    except Exception as e:
        log.exception("stream error: %s", e)

    await flush()
    rc = await process.wait()
    state["status"] = "stopped"
    state["exit_code"] = rc
    await safe_send(
        ctx,
        chat_id,
        f"🛑 <b>Bot process exited</b> (code <code>{rc}</code>)\n"
        "Send new credentials to restart, or /stop.",
        parse_mode=ParseMode.HTML,
    )


async def stop_user_process(state: dict):
    process = state.get("process")
    if process and process.returncode is None:
        try:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
        except Exception as e:
            log.warning("stop error: %s", e)
    task = state.get("task")
    if task and not task.done():
        task.cancel()
        try:
            await task
        except Exception:
            pass


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    state = SESSIONS.setdefault(chat_id, {})

    if not state.get("joined"):
        if await is_member(ctx, user_id):
            state["joined"] = True
        else:
            await update.message.reply_text(
                NOT_JOINED, parse_mode=ParseMode.HTML, reply_markup=main_keyboard()
            )
            return

    if ":" not in text:
        await update.message.reply_text(INVALID_FORMAT, parse_mode=ParseMode.HTML)
        return

    uid, _, password = text.partition(":")
    uid = uid.strip()
    password = password.strip()
    if not uid or not password:
        await update.message.reply_text(INVALID_FORMAT, parse_mode=ParseMode.HTML)
        return

    if state.get("process") and state["process"].returncode is None:
        await update.message.reply_text(
            "🛑 <b>Stopping previous session...</b>", parse_mode=ParseMode.HTML
        )
        await stop_user_process(state)

    user_dir = os.path.join(SESSIONS_DIR, str(chat_id))
    os.makedirs(user_dir, exist_ok=True)
    bot_txt_path = os.path.join(user_dir, "bot.txt")
    token_json_path = os.path.join(user_dir, "token.json")

    with open(bot_txt_path, "w") as f:
        json.dump({uid: password}, f)

    loading = await update.message.reply_text(
        "⚡ <b>Igniting Hayato engine...</b>", parse_mode=ParseMode.HTML
    )
    await play_loading(loading, "Logging into Garena...", delay=0.2)
    try:
        await loading.edit_text(
            "🚀 <b>Bot is starting!</b>\n📡 <i>Streaming live logs below</i> 👇",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    env = os.environ.copy()
    env["BOT_TXT_PATH"] = bot_txt_path
    env["TOKEN_JSON_PATH"] = token_json_path
    env["PYTHONUNBUFFERED"] = "1"

    try:
        process = await asyncio.create_subprocess_exec(
            "python",
            "main.py",
            cwd=BOT_DIR,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>Failed to start bot:</b> <code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    state["process"] = process
    state["status"] = "starting"
    state["started_at"] = time.time()
    state["uid"] = uid
    state["last_error"] = None
    state["exit_code"] = None
    state["online_at"] = None
    state["task"] = asyncio.create_task(stream_subprocess(process, ctx, chat_id, state))


def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


STATUS_LABEL = {
    "idle": "⚪ Idle",
    "starting": "🟡 Starting",
    "logging_in": "🟡 Logging in",
    "online": "🟢 Online",
    "restarting": "🟠 Restarting",
    "error": "🔴 Error",
    "stopped": "⚫ Stopped",
}


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = SESSIONS.get(chat_id, {})
    status = state.get("status", "idle")
    label = STATUS_LABEL.get(status, status)
    uid = state.get("uid", "—")
    started_at = state.get("started_at")
    online_at = state.get("online_at")
    process = state.get("process")
    pid = process.pid if process and process.returncode is None else "—"
    last_error = state.get("last_error") or "—"

    uptime = fmt_duration(time.time() - started_at) if started_at else "—"
    online_for = fmt_duration(time.time() - online_at) if online_at else "—"

    msg = (
        "📊━━━━━━━━━━━━━━━━━📊\n"
        "🛰️  <b>SESSION STATUS</b>  🛰️\n"
        "📊━━━━━━━━━━━━━━━━━📊\n\n"
        f"<b>State:</b> {label}\n"
        f"<b>UID:</b> <code>{html_escape(str(uid))}</code>\n"
        f"<b>PID:</b> <code>{pid}</code>\n"
        f"<b>Uptime:</b> {uptime}\n"
        f"<b>Online for:</b> {online_for}\n"
        f"<b>Channel:</b> {CHANNEL}\n\n"
        f"<b>Last error:</b> <code>{html_escape(last_error)}</code>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📖━━━━━━━━━━━━━━━━━📖\n"
        "🤖  <b>HAYATO LEVEL UP BOT V2.0</b>  🤖\n"
        "📖━━━━━━━━━━━━━━━━━📖\n\n"
        "<b>Telegram commands</b>\n"
        "<code>/start</code>  – show welcome\n"
        "<code>/status</code> – show session status\n"
        "<code>/stop</code>   – stop your bot\n"
        "<code>/help</code>   – this menu\n\n"
        "<b>Send credentials</b> as:\n"
        "<code>UID:PASSWORD</code>\n\n"
        "<b>In-game commands</b> (after online)\n"
        "<code>/lw &lt;team_code&gt;</code> – auto level up\n"
        "<code>/stop_auto</code> – stop auto level up\n"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = SESSIONS.get(chat_id, {})
    process = state.get("process")
    if process and process.returncode is None:
        await update.message.reply_text(
            "🛑 <b>Stopping the bot...</b>", parse_mode=ParseMode.HTML
        )
        await stop_user_process(state)
        await update.message.reply_text(
            "✅ <b>Bot stopped successfully</b>\n\nSend new credentials to start again.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            "ℹ️ <b>No bot is running.</b>\nSend credentials to start.",
            parse_mode=ParseMode.HTML,
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(cb_continue, pattern="^continue$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info("Bot polling started — channel=%s", CHANNEL)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
