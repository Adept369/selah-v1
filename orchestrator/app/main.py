# app/main.py
from fastapi import FastAPI, Request, HTTPException
from app.orchestration.dispatcher import dispatch_command
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")