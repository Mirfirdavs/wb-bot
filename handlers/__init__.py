# handlers/__init__.py

# Импортируем все модули с обработчиками в правильном порядке
from . import start  # команды /start, /ping
from . import admin  # команда /admin
from . import tax  # FSM обработчики налогов
from . import files  # FSM обработчики файлов
from . import referral
from . import donate
from . import reports  # обработчики отчетов (должен быть последним!)

__all__ = ["register_handlers"]


def register_handlers():
    """Функция для явной регистрации всех обработчиков"""
    # Просто импортируем модули - декораторы @dp.message сами зарегистрируют обработчики
