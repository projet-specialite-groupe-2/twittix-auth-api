import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    BACKEND_URL: str = os.getenv("BACKEND_URL")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    BASE_URL: str = os.getenv("BASE_URL")
    API_KEY: str = os.getenv("API_KEY")


settings = Settings()
