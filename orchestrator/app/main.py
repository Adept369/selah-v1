import logging
from fastapi import FastAPI, Request, Header, HTTPException

from telegram import Bot
from telegram.error import TelegramError

from app.core.config import settings
from app.orchestration.master_agent import MasterAgent
from app.llm.clients import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_TOKEN)
llm_client = LLMClient(settings)
master = MasterAgent(llm_client=llm_client)

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

    # 2) parse update #
    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return {"status": "ignored"}

    chat_id = msg["chat"]["id"]
    # 3) get a reply from MasterAgent
    reply_text = await master.run(update)

    # 4) send to Telegram
    if reply_text:
        try:
            await bot.send_message(chat_id=chat_id, text=reply_text)
        except TelegramError as e:
            logger.error("Telegram send failed: %s", e)

    # 5) return something *non-null* so curl sees it
    return {"status": "ok", "reply": reply_text}
