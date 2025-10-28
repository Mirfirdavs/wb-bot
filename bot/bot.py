from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from config import Config


def create_bot() -> Bot:
    """Создание экземпляра бота"""
    return Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


# Глобальный экземпляр бота
bot = create_bot()
