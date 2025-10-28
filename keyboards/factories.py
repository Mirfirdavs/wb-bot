from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardFactory:
    """Фабрика клавиатур для бота"""

    @staticmethod
    def get_tax_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура выбора налоговой ставки"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1%", callback_data="tax_1"),
                    InlineKeyboardButton(text="6%", callback_data="tax_6"),
                    InlineKeyboardButton(text="7%", callback_data="tax_7"),
                ],
                [
                    InlineKeyboardButton(text="8%", callback_data="tax_8"),
                    InlineKeyboardButton(text="Другое", callback_data="tax_other"),
                ],
            ]
        )

    @staticmethod
    def get_analysis_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура после формирования отчета"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Детальный Excel", callback_data="get_excel"
                    ),
                    InlineKeyboardButton(
                        text="📈 Краткий PDF", callback_data="get_pdf"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🔄 Новый расчет", callback_data="new_calculation"
                    ),
                ],
            ]
        )
