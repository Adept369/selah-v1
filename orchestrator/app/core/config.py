from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv



load_dotenv()    # <-- picks up Selah/.env
class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    WEBHOOK_SECRET: str
    RABBITMQ_URL: str
    N8N_WEBHOOK_URL: str
     # ——— New LLM Backend Settings ——————————————————————————————
    LLM_BACKEND: str = "openai"                # either "openai" or "llama"
    OPENAI_API_KEY: Optional[str] = None       # if you use OpenAI
    OPENAI_MODEL_NAME: str = "gpt-3.5-turbo"   # default OpenAI model
    LLAMA_MODEL_PATH: Optional[str] = None     # if you use llama-cpp, e.g. "/models/ggml-model.bin"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
