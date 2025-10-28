from .start import *
from .tax import *
from .files import *
from .reports import *
from .admin import *  

__all__ = ["register_handlers"]


def register_handlers():
    """Регистрация всех обработчиков"""
    # Импорты здесь для избежания циклических зависимостей
    from . import start, tax, files, reports, admin  
