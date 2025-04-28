# orchestrator/app/main.py

import logging
import os
import tempfile

from fastapi import FastAPI, Request, Header, HTTPException
from telegram import Bot
from telegram.error import TelegramError
from gtts import gTTS

from app.core.config import settings
from app.orchestration.master_agent import MasterAgent
from app.llm.clients import LLMClient
from app.agents.file_conversion_agent.file_conversion_agent import FileConversionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# — Initialize clients & agents —
bot = Bot(token=settings.TELEGRAM_TOKEN)
llm_client = LLMClient(settings)
master = MasterAgent(llm_client=llm_client)
audio_agent = FileConversionAgent(llm_client=None)  # only uses audio_to_text

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    secret: str = Header(None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    # 1) optional secret check
    if settings.WEBHOOK_SECRET and secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2) parse incoming update
    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return {"status": "ignored"}

    chat_id = msg["chat"]["id"]

    # 3) detect voice vs text
    if "voice" in msg:
        # download the voice note
        file_id = msg["voice"]["file_id"]
       

         # 1) fetch the File object
        tg_file = await bot.get_file(file_id)
        # 2) write it to a temp .ogg
        tf = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        await tg_file.download_to_drive(tf.name)
        tf.close()
        logger.info("Downloaded voice note to %s", tf.name)

        # transcribe
        try:
            user_input = audio_agent.audio_to_text(tf.name)
            logger.info("Transcription result: %r", user_input)
        finally:
            os.unlink(tf.name)
    else:
        user_input = msg.get("text", "")

    # 4) route to MasterAgent
    fake_update = {"message": {"chat": {"id": chat_id}, "text": user_input}}
    reply_text = await master.run(fake_update)

    # 5) generate witty one-liner on the original user_input
    witty = None
    if user_input:
        try:
            witty = llm_client.generate(
                prompt=f"Give me a short, witty one-liner about: {user_input}",
                max_tokens=50,
                temperature=0.8
            ).strip()
            logger.info("Witty line: %r", witty)
        except Exception as e:
            logger.error("Failed to generate witty line: %s", e)

    # 6a) send the full answer back as text
    if reply_text:
        try:
            await bot.send_message(chat_id=chat_id, text=reply_text)
        except TelegramError as e:
            logger.error("Failed to send text reply: %s", e)

    # 6b) if we have a witty line, TTS it and send as voice note
    if witty:
        try:
            tts = gTTS(witty)
            mp3_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tts.write_to_fp(mp3_file)
            mp3_file.flush()
            mp3_file.close()

            with open(mp3_file.name, "rb") as f:
                await bot.send_voice(chat_id=chat_id, voice=f)
        except Exception as e:
            logger.error("Failed to send witty voice note: %s", e)
        finally:
            if os.path.exists(mp3_file.name):
                os.unlink(mp3_file.name)

    # 7) always return non-null JSON
    return {"status": "ok", "reply": reply_text, "witty": witty}
