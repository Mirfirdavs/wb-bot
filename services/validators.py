from typing import Tuple
import pandas as pd
from aiogram.types import Message
from config import Config


class FileValidator:
    """Класс для валидации файлов"""

    @staticmethod
    def validate_file_size(message: Message) -> bool:
        """Проверка размера файла"""
        if not message.document:
            return False
        return message.document.file_size <= Config.MAX_FILE_SIZE

    @staticmethod
    def validate_file_type(message: Message) -> bool:
        """Проверка типа файла"""
        if not message.document:
            return False
        filename = message.document.file_name or ""
        return filename.endswith((".xlsx", ".xls"))

    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: list) -> Tuple[bool, list]:
        """Проверка наличия необходимых колонок"""
        df.columns = df.columns.str.strip()
        missing_columns = [col for col in required_columns if col not in df.columns]
        return len(missing_columns) == 0, missing_columns
