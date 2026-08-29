import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
PUBLIC_URL = os.environ["PUBLIC_URL"].rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
MAX_MB = int(os.getenv("MAX_MB", "25"))

PRESETS = {
    "house": ("Хаус", "highpass=f=35,acompressor=threshold=-18dB:ratio=3, bass=g=4, aecho=0.8:0.88:60:0.25"),
    "techno": ("Техно", "highpass=f=45,acompressor=threshold=-20dB:ratio=4, bass=g=6, aecho=0.8:0.9:90:0.2"),
    "jungle": ("Джангл", "highpass=f=45,atempo=1.08,bass=g=3,aecho=0.8:0.8:35:0.25"),
    "hiphop": ("Хип-хоп", "highpass=f=35,lowpass=f=15000,bass=g=5,acompressor=threshold=-16dB:ratio=3"),
    "lofi": ("Лоу-фай", "lowpass=f=6000,highpass=f=100,bass=g=2,aecho=0.8:0.7:80:0.35"),
    "poprock": ("Поп-рок", "highpass=f=40,acompressor=threshold=-18dB:ratio=2.5,treble=g=3,bass=g=3"),
}

app = FastAPI()
tg = Application.builder().token(BOT_TOKEN).build()


def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хаус", callback_data="house"), InlineKeyboardButton("Техно", callback_data="techno")],
        [InlineKeyboardButton("Джангл", callback_data="jungle"), InlineKeyboardButton("Хип-хоп", callback_data="hiphop")],
        [InlineKeyboardButton("Лоу-фай", callback_data="lofi"), InlineKeyboardButton("Поп-рок", callback_data="poprock")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправьте MP3, WAV или M4A, затем выберите стиль ремикса.", reply_markup=keyboard())


async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["preset"] = query.data
    await query.message.reply_text(f"Выбран стиль: {PRESETS[query.data][0]}. Теперь отправьте аудиофайл.")


async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.audio or update.message.document
    if not doc:
        return
    filename = getattr(doc, "file_name", None) or getattr(doc, "filename", None) or "input.mp3"
    if Path(filename).suffix.lower() not in {".mp3", ".wav", ".m4a", ".ogg", ".flac"}:
        await update.message.reply_text("Поддерживаются MP3, WAV, M4A, OGG и FLAC.")
        return
    if getattr(doc, "file_size", 0) > MAX_MB * 1024 * 1024:
        await update.message.reply_text(f"Файл слишком большой. Максимум — {MAX_MB} МБ.")
        return
    preset = context.user_data.get("preset", "house")
    work = Path(tempfile.mkdtemp(prefix="remix-"))
    try:
        src = work / "input" / Path(filename).name
        out = work / "remix.mp3"
        src.parent.mkdir()
        f = await tg.bot.get_file(doc.file_id)
        await f.download_to_drive(src)
        label, filterspec = PRESETS[preset]
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", str(src), "-af", filterspec,
            "-codec:a", "libmp3lame", "-b:a", "192k", str(out),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        try:
            logs, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
        except asyncio.TimeoutError:
            proc.kill(); await proc.wait()
            await update.message.reply_text("Обработка заняла слишком много времени.")
            return
        if proc.returncode != 0 or not out.exists():
            await update.message.reply_text("Не удалось обработать файл. Проверьте формат аудио.")
            return
        await update.message.reply_audio(audio=out.open("rb"), caption=f"Готово: {label}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


async def setup():
    await tg.initialize()
    await tg.bot.set_webhook(f"{PUBLIC_URL}/telegram/{BOT_TOKEN}")
    await tg.start()


async def shutdown():
    await tg.stop()
    await tg.shutdown()


tg.add_handler(CommandHandler("start", start))
tg.add_handler(CallbackQueryHandler(choose))
tg.add_handler(MessageHandler(filters.AUDIO | filters.Document.ALL, audio))


@app.on_event("startup")
async def startup():
    await setup()


@app.on_event("shutdown")
async def stop():
    await shutdown()


@app.get("/")
def health():
    return {"status": "ok", "service": "music-remix-bot"}


@app.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != BOT_TOKEN:
        return {"ok": False}
    update = Update.de_json(await request.json(), tg.bot)
    await tg.process_update(update)
    return {"ok": True}
