from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    WEBHOOK_SECRET: str
    RABBITMQ_URL: str
    N8N_WEBHOOK_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
