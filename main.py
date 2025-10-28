import asyncio
from bot.bot import bot
from bot.dispatcher import dp
from handlers import register_handlers
from services.session_manager import session_manager
from utils.logger import logger


async def main():
    """Основная функция запуска бота"""
    # Регистрация всех обработчиков
    register_handlers()

    logger.info("Starting WB Analytics Bot...")

    # Запуск фоновых задач
    asyncio.create_task(scheduled_cleanup())

    # Запуск бота
    await dp.start_polling(bot)


async def scheduled_cleanup():
    """Регулярная очистка устаревших сессий"""
    while True:
        await asyncio.sleep(3600)  # Каждый час
        cleaned_count = session_manager.cleanup_expired()
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired sessions")


if __name__ == "__main__":
    asyncio.run(main())
