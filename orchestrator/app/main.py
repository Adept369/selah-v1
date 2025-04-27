# app/main.py

import logging
from typing import Optional

from fastapi import FastAPI, Request, Header, HTTPException
from telegram import Bot
from telegram.error import TelegramError

from app.core.config import settings
from app.orchestration.dispatcher import dispatch_command

# ——— Logging setup ———————————————————————————————————————————————————
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"🔑 WEBHOOK_SECRET is: {settings.WEBHOOK_SECRET!r}")

# ——— Telegram Bot client ————————————————————————————————————————————————
bot = Bot(token=settings.TELEGRAM_TOKEN)

# ——— FastAPI app ——————————————————————————————————————————————————————
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    secret: Optional[str] = Header(None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    # 1) If the header is present but wrong, reject; otherwise continue
    if secret is not None and secret != settings.WEBHOOK_SECRET:
        logger.warning("Forbidden request with secret: %r", secret)
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2) Dump raw bytes so we can inspect any 422s
    raw = await request.body()
    logger.info("Raw body: %r", raw)

    # 3) Parse JSON
    try:
        update = await request.json()
    except Exception as e:
        logger.error("JSON decode error: %s", e)
        raise HTTPException(status_code=400, detail="Bad JSON")

    # 4) Grab the incoming message (ignore edits, channels, etc.)
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        logger.info("No message found; ignoring update.")
        return {"status": "ignored"}

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    logger.info("Got update from chat %s: %r", chat_id, text)

    # 5) Dispatch through your orchestration layer
    try:
        reply = await dispatch_command(update)
    except Exception:
        logger.exception("dispatch_command failed")
        reply = "Sorry, something went wrong."

    # 6) If you got something back, send it
    if reply:
        try:
            await bot.send_message(chat_id=chat_id, text=reply)
            logger.info("Sent reply to chat %s: %r", chat_id, reply)
        except TelegramError as te:
            logger.error("Failed to send message: %s", te)

    return {"status": "ok"}
