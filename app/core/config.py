import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    BACKEND_URL: str = os.getenv("BACKEND_URL")


settings = Settings()
