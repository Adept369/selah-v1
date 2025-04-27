# orchestrator/app/core/config.py

import os
from dotenv import load_dotenv
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env into os.environ
load_dotenv()

class Settings(BaseSettings):
    # Telegram settings
    TELEGRAM_TOKEN: str
    WEBHOOK_SECRET: str

    # LLM backend settings
    LLM_BACKEND: str = "openai"           # "openai" or "llama"
    OPENAI_API_KEY: Optional[str] = None
    LLAMA_MODEL_PATH: Optional[str] = None

    # RabbitMQ
    RABBITMQ_URL: str

    # n8n automation
    N8N_WEBHOOK_URL: str
    N8N_USER: str
    N8N_PASSWORD: str

    # Pinecone—case‐law index
    CASELAW_PINECONE_API_KEY: str
    CASELAW_PINECONE_ENVIRONMENT: str
    CASELAW_PINECONE_INDEX: str

    # Pinecone—memo index
    MEMO_PINECONE_API_KEY: str
    MEMO_PINECONE_ENVIRONMENT: str
    MEMO_PINECONE_INDEX: str

    # Pinecone—generic
    PINECONE_API_KEY: str
    PINECONE_ENV: str

    model_config = SettingsConfigDict(
        extra="ignore"  # ignore any undeclared variables
    )

# Instantiate settings (will raise ValidationError if any required field is missing)
settings = Settings()
