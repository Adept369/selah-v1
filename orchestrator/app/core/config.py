# orchestrator/app/core/config.py

from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_TOKEN: str
    WEBHOOK_SECRET: str

    # LLM
    LLM_BACKEND: Literal["openai", "llama"] = "openai"
    OPENAI_API_KEY: Optional[str] = None
    LLAMA_MODEL_PATH: Optional[str] = None

    # RabbitMQ
    RABBITMQ_URL: str

    # n8n
    N8N_WEBHOOK_URL: str
    N8N_USER: str
    N8N_PASSWORD: str

    # Pinecone — case-law index
    CASELAW_PINECONE_API_KEY: str
    CASELAW_PINECONE_ENVIRONMENT: str
    CASELAW_PINECONE_INDEX: str

    # Pinecone — memo index
    MEMO_PINECONE_API_KEY: str
    MEMO_PINECONE_ENVIRONMENT: str
    MEMO_PINECONE_INDEX: str

    # Pinecone — generic
    PINECONE_API_KEY: str
    PINECONE_ENV: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
