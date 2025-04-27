import logging 
from fastapi import FastAPI, Request, Header, HTTPException

from telegram import Bot
from telegram.error import TelegramError
from typing import Tuple
from app.core.config import settings

from app.llm.clients import LLMClient
from app.orchestration.registry import build_registry

# ——— Logging setup —————————————————————————————————————————————————————————————
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        # build_registry returns your agent dict
        self.registry = build_registry(llm_client)

    def classify_intent(self, text: str) -> str:
        lower = text.lower()
        if any(k in lower for k in ["sovereignty", "case", "statute", "law", "precedent"]):
            return "case_law_scholar"
        if "memo" in lower or "draft" in lower:
            return "memo_drafter"
        if any(k in lower for k in ["remind", "schedule", "date", "time"]):
            return "n8n_scheduler"
        if lower.startswith("convert "):
            return "file_conversion"
        
         # --- conversion requests ---
        if "convert " in lower or " to pdf" in lower or " to docx" in lower \
           or " to csv" in lower or " to xlsx" in lower or "transcribe" in lower \
           or "audio to text" in lower:
            return "file_conversion"

        # --- case-law research ---
        if any(k in lower for k in ["sovereignty", "case", "statute", "law", "precedent"]):
            return "case_law_scholar"

        # --- memo drafting ---
        if "memo" in lower or "draft" in lower:
            return "memo_drafter"

        # --- scheduling via n8n ---
        if any(k in lower for k in ["remind", "schedule", "date", "time"]):
            return "n8n_scheduler"

        return "help"
    



    def parse(self, text: str) -> Tuple[str, str]:
        agent_key = self.classify_intent(text)
        return agent_key, text

    async def run(self, update: dict) -> str:
        msg = update.get("message", {})
        text = msg.get("text", "")
        if not text:
            return "Please send a text message."
        agent_key, query = self.parse(text)
        agent = self.registry.get(agent_key)
        if not agent:
            return "⚠️ Sorry, I don't know how to help with that yet."
        logger.info(f"MasterAgent routing to '{agent_key}' for: {query!r}")
        result = agent.run(query)
        if hasattr(result, "__await__"):
            result = await result
        return result


# ——— Telegram Bot client —————————————————————————————————————————————————————————
bot = Bot(token=settings.TELEGRAM_TOKEN)

# ——— LLM client & MasterAgent ——————————————————————————————————————————————————————
llm_client = LLMClient(settings)
master = MasterAgent(llm_client=llm_client)

# ——— FastAPI app ———————————————————————————————————————————————————————————————
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

    # 2) parse JSON update
    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 3) ignore non‐message updates
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return {"status": "ignored"}

    chat_id = msg["chat"]["id"]

    # 4) ask the MasterAgent for a reply
    reply_text = await master.run(update)

    # 5) send the reply to Telegram
    if reply_text:
        try:
            await bot.send_message(chat_id=chat_id, text=reply_text)
        except TelegramError as e:
            logger.error("Telegram send failed: %s", e)

    # 6) return something non‐null so test clients (and curl) see it
    return {"status": "ok", "reply": reply_text}
