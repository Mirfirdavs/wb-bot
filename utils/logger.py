import logging
from config import Config


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(**Config.LOGGING_CONFIG)
    return logging.getLogger(__name__)


# Глобальный логгер
logger = setup_logging()
