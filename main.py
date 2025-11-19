import os
import subprocess
import asyncio
import tempfile

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultCachedGif,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    filters,
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
INLINE_STORAGE_CHAT_ID = int(os.getenv("INLINE_STORAGE_CHAT_ID", "0") or "0")

BASE_VIDEOS_DIR = "base_videos"
FONT_FILE = os.path.join("fonts", "font.ttf")
DEFAULT_VIDEO_PATH = os.path.join(BASE_VIDEOS_DIR, "default.mp4")

TEXT_COLOR = "white"
BORDER_COLOR = "black"
FONT_SIZE = 48

ASK_NAME = 1
WAIT_SOURCE = 2

def ensure_directories():
    os.makedirs(BASE_VIDEOS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(FONT_FILE), exist_ok=True)


def list_base_videos():
    files = [
        f for f in os.listdir(BASE_VIDEOS_DIR)
        if f.lower().endswith((".mp4", ".mov", ".mkv"))
    ]
    return [f for f in files if f != "default.mp4"]


def generate_hi_gif(name: str, source_video: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp.close()
    out_path = tmp.name

    text = f"Hi {name}".replace("'", "")

    drawtext = (
        f"drawtext=fontfile='{FONT_FILE}':"
        f"text='{text}':"
        f"fontcolor={TEXT_COLOR}:"
        f"fontsize={FONT_SIZE}:"
        f"borderw=3:bordercolor={BORDER_COLOR}:"
        f"x=(w-text_w)/2:y=h-text_h-40"
    )

    vf_filter = (
        f"crop=min(iw\\,ih):min(iw\\,ih),"
        f"scale=512:512,"
        f"{drawtext}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", source_video,
        "-vf", vf_filter,
        "-r", "15",
        "-loop", "0",
        out_path,
    ]

    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if completed.returncode != 0:
        try:
            os.remove(out_path)
        except OSError:
            pass
        raise RuntimeError(
            f"ffmpeg failed (normal): {completed.stderr.decode('utf-8', errors='ignore')}"
        )

    return out_path


def generate_hi_gif_inline(name: str, source_video: str) -> str:

    tmp = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp.close()
    out_path = tmp.name

    text = f"Hi {name}".replace("'", "")

    drawtext = (
        f"drawtext=fontfile='{FONT_FILE}':"
        f"text='{text}':"
        f"fontcolor={TEXT_COLOR}:"
        f"fontsize={FONT_SIZE}:"
        f"borderw=3:bordercolor={BORDER_COLOR}:"
        f"x=(w-text_w)/2:y=h-text_h-30"
    )

    vf_filter = (
        f"scale=256:256:force_original_aspect_ratio=decrease,"
        f"pad=256:256:(256-iw)/2:(256-ih)/2,"
        f"{drawtext}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-t", "3",
        "-i", source_video,
        "-vf", vf_filter,
        "-r", "10",
        "-loop", "0",
        out_path,
    ]

    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if completed.returncode != 0:
        try:
            os.remove(out_path)
        except OSError:
            pass
        raise RuntimeError(
            f"ffmpeg failed (inline): {completed.stderr.decode('utf-8', errors='ignore')}"
        )

    return out_path


async def send_hi_gif(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    name: str,
    source_video_path: str,
):
    gif_path = None
    try:
        gif_path = await asyncio.to_thread(generate_hi_gif, name, source_video_path)
        with open(gif_path, "rb") as f:
            await update.effective_message.reply_animation(
                f,
                caption=f"Here’s a hi for {name} ✨",
            )
        await update.effective_message.reply_text("Done. Just forward this GIF to them. 😉")
    finally:
        if gif_path and os.path.exists(gif_path):
            try:
                os.remove(gif_path)
            except OSError:
                pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Hey 👋\nWho do you want to say hi to?\n\nSend me their name:"
    )
    return ASK_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Send a real name, not an empty message 😅")
        return ASK_NAME

    context.user_data["name"] = name

    base_videos = list_base_videos()
    keyboard = []
    for filename in base_videos:
        label = os.path.splitext(filename)[0]
        keyboard.append(
            [InlineKeyboardButton(label, callback_data=f"base:{filename}")]
        )

    if not keyboard:
        text_choice = (
            f"Nice. I’ll say hi to {name}.\n\n"
            "Now send me a video to use as background, "
            "or send /default to use the default cat."
        )
        reply_markup = None
    else:
        text_choice = (
            f"Nice. I’ll say hi to {name}.\n\n"
            "Now either:\n"
            "• Send me a video (MP4/GIF) to use as background\n"
            "• Or tap one of my cats below\n"
            "• Or send /default to use the default cat"
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text_choice, reply_markup=reply_markup)

    return WAIT_SOURCE


async def handle_default(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = context.user_data.get("name")
    if not name:
        await update.message.reply_text("Use /start first to tell me the name.")
        return ConversationHandler.END

    if not os.path.exists(DEFAULT_VIDEO_PATH):
        await update.message.reply_text(
            "default.mp4 is missing in base_videos/. Add it and try again."
        )
        return ConversationHandler.END

    await update.message.reply_text("Using the default cat… 🐱")
    await send_hi_gif(update, context, name, DEFAULT_VIDEO_PATH)
    return ConversationHandler.END


async def handle_base_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    name = context.user_data.get("name")
    if not name:
        await query.edit_message_text("Use /start first to tell me the name.")
        return ConversationHandler.END

    data = query.data
    _, filename = data.split(":", 1)
    video_path = os.path.join(BASE_VIDEOS_DIR, filename)

    if not os.path.exists(video_path):
        await query.edit_message_text("That video is missing on the server.")
        return ConversationHandler.END

    await query.edit_message_text(f"Nice choice. Generating your GIF with {filename}… 🎬")

    fake_update = Update(update.update_id, message=query.message)
    await send_hi_gif(fake_update, context, name, video_path)

    return ConversationHandler.END


async def handle_user_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = context.user_data.get("name")
    if not name:
        await update.message.reply_text("Use /start first to tell me the name.")
        return ConversationHandler.END

    msg = update.message

    tg_file = None
    if msg.video:
        tg_file = msg.video
    elif msg.animation:
        tg_file = msg.animation
    elif msg.document and msg.document.mime_type and "video" in msg.document.mime_type:
        tg_file = msg.document

    if not tg_file:
        await update.message.reply_text("Send a valid video or use /default.")
        return WAIT_SOURCE

    file = await tg_file.get_file()

    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.close()
    temp_video_path = tmp.name

    try:
        await file.download_to_drive(temp_video_path)
        await update.message.reply_text("Got your video. Generating your GIF… 🎬")
        await send_hi_gif(update, context, name, temp_video_path)
    finally:
        if os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except OSError:
                pass

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled. Use /start whenever you’re ready again.")
    return ConversationHandler.END

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if INLINE_STORAGE_CHAT_ID == 0:
        await update.inline_query.answer([], cache_time=1)
        return

    query = update.inline_query.query.strip()
    if not query:
        return

    name = query

    if not os.path.exists(DEFAULT_VIDEO_PATH):
        await update.inline_query.answer([], cache_time=1)
        return

    cache = context.application.bot_data.setdefault("inline_cache", {})
    gif_file_id = cache.get(name)

    if not gif_file_id:
        gif_path = await asyncio.to_thread(
            generate_hi_gif_inline, name, DEFAULT_VIDEO_PATH
        )

        try:
            with open(gif_path, "rb") as f:
                msg = await context.bot.send_animation(
                    chat_id=INLINE_STORAGE_CHAT_ID,
                    animation=f,
                    caption=f"Hi {name}",
                )
            gif_file_id = msg.animation.file_id
            cache[name] = gif_file_id
        finally:
            if os.path.exists(gif_path):
                try:
                    os.remove(gif_path)
                except OSError:
                    pass

    result = InlineQueryResultCachedGif(
        id=f"hi-{name}",
        gif_file_id=gif_file_id,
        title=f"Hi {name}",
        caption=f"Here’s a hi for {name} ✨",
    )

    try:
        await update.inline_query.answer([result], cache_time=0)
    except Exception as e:
        print("Error answering inline query:", e)

def main():
    ensure_directories()

    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN env var not set.")

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            WAIT_SOURCE: [
                MessageHandler(
                    filters.VIDEO
                    | filters.ANIMATION
                    | filters.Document.VIDEO,
                    handle_user_video,
                ),
                CommandHandler("default", handle_default),
                CallbackQueryHandler(handle_base_choice, pattern=r"^base:"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("default", handle_default))

    application.add_handler(InlineQueryHandler(inline_query))

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()