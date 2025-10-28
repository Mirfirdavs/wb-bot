import os
import logging
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация приложения"""

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    PROCESSING_TIMEOUT = 300  # 5 минут
    DEFAULT_TAX_RATE = 6.0

    # 🔐 АДМИНСКИЕ НАСТРОЙКИ
    ADMIN_IDS = (
        list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
        if os.getenv("ADMIN_IDS")
        else []
    )
    ADMIN_LOG_CHAT_ID = os.getenv("ADMIN_LOG_CHAT_ID")  # Для логов

    # Цветовая схема для визуализации
    COLORS = {
        "primary": "#2E86AB",
        "success": "#A3D9B1",
        "warning": "#F9C74F",
        "danger": "#F94144",
        "dark": "#264653",
    }

    # Настройки логирования
    LOGGING_CONFIG = {
        "level": logging.INFO,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "handlers": [
            logging.FileHandler("wb_analytics_bot.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    }


if not Config.BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле!")
