import os

class Settings:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    DATABASE_URI = os.getenv("DATABASE_URI", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

settings = Settings()