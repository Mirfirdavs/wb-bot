from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AdminKeyboard:
    """Клавиатуры для админ-панели"""

    @staticmethod
    def get_admin_main() -> InlineKeyboardMarkup:
        """Основная клавиатура админки"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
        )
        builder.row(
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
            InlineKeyboardButton(
                text="📁 Экспорт данных", callback_data="admin_export"
            ),
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh"),
            InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close"),
        )

        return builder.as_markup()

    @staticmethod
    def get_stats_refresh() -> InlineKeyboardMarkup:
        """Клавиатура для обновления статистики"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_stats"),
            InlineKeyboardButton(
                text="📊 Детальная stats", callback_data="admin_detailed_stats"
            ),
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"),
        )
        return builder.as_markup()

    @staticmethod
    def get_export_options() -> InlineKeyboardMarkup:
        """Клавиатура выбора типа экспорта"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(text="📋 Excel", callback_data="export_excel"),
            InlineKeyboardButton(text="📄 PDF", callback_data="export_pdf"),
        )
        builder.row(
            InlineKeyboardButton(text="📊 Графики", callback_data="export_charts"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"),
        )

        return builder.as_markup()

    @staticmethod
    def get_broadcast_confirm() -> InlineKeyboardMarkup:
        """Клавиатура подтверждения рассылки"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="✅ Отправить", callback_data="broadcast_confirm"
            ),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="broadcast_edit"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back"),
        )

        return builder.as_markup()

    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """Простая кнопка назад"""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"))
        return builder.as_markup()
