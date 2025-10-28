from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


def create_dispatcher() -> Dispatcher:
    """Создание диспетчера"""
    storage = MemoryStorage()
    return Dispatcher(storage=storage)


# Глобальный экземпляр диспетчера
dp = create_dispatcher()
