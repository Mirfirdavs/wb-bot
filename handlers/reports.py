from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    Message,
    CallbackQuery,
)
from datetime import datetime

from bot.dispatcher import dp
from services.session_manager import session_manager
from services.excel_formatter import ExcelFormatter
from services.report_generator import ReportGenerator
from keyboards.factories import KeyboardFactory
from states.analytics import AnalyticsState
from utils.logger import logger


@dp.callback_query(F.data == "get_excel")
async def send_excel_report(callback: CallbackQuery):
    """Отправка детального Excel отчета"""
    session = session_manager.get_session(callback.from_user.id)

    if session.final_df is None:
        await callback.answer("⚠️ Сначала сформируйте отчет!", show_alert=True)
        return

    try:
        processing_msg = await callback.message.answer(
            "⏳ <b>Формирую Excel отчет...</b>"
        )

        # Форматирование и создание Excel
        excel_file = ExcelFormatter.apply_business_formatting(session.final_df)
        excel_buffered = BufferedInputFile(
            excel_file.getvalue(),
            filename=f"WB_Analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        )

        await processing_msg.delete()
        await callback.message.answer_document(
            excel_buffered,
            caption="📊 <b>Детальный финансовый отчет</b>\n"
            "• Все финансовые показатели\n"
            "• Профессиональное форматирование\n"
            "• Готово для бизнес-анализа",
        )

    except Exception as e:
        logger.error(f"Error generating Excel: {e}")
        await callback.message.answer("❌ Ошибка при создании Excel отчета")


@dp.callback_query(F.data == "get_pdf")
async def send_pdf_report(callback: CallbackQuery):
    """Отправка краткого PDF отчета"""
    session = session_manager.get_session(callback.from_user.id)

    if session.final_df is None:
        await callback.answer("⚠️ Сначала сформируйте отчет!", show_alert=True)
        return

    try:
        processing_msg = await callback.message.answer(
            "⏳ <b>Формирую PDF отчет...</b>"
        )

        # Создание PDF
        pdf_file = ReportGenerator.generate_comprehensive_pdf(session.final_df)
        pdf_buffered = BufferedInputFile(
            pdf_file.getvalue(),
            filename=f"WB_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        )

        await processing_msg.delete()
        await callback.message.answer_document(
            pdf_buffered,
            caption="📈 <b>Краткий аналитический отчет</b>\n"
            "• Визуализация ключевых метрик\n"
            "• ТОП товары по прибыли\n"
            "• Распределение доходов",
        )

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        await callback.message.answer("❌ Ошибка при создании PDF отчета")


@dp.callback_query(F.data == "new_calculation")
async def new_calculation(callback: CallbackQuery, state: FSMContext):
    """Начать новый расчет"""
    session = session_manager.get_session(callback.from_user.id)
    session.main_df = None
    session.final_df = None

    await state.set_state(AnalyticsState.waiting_for_tax)
    await callback.message.edit_text(
        "🔄 <b>Начинаем новый расчет!</b>\n\n📊 Выберите налоговую ставку:",
        reply_markup=KeyboardFactory.get_tax_keyboard(),
    )
    await callback.answer()


# Обработчик всех остальных сообщений
@dp.message()
async def handle_other_messages(message: Message):
    """Обработчик всех остальных сообщений"""
    if message.document:
        await message.answer(
            "⚠️ <b>Сначала выберите налоговую ставку!</b>\n"
            "Используйте команду /start для начала работы."
        )
    else:
        await message.answer(
            "🤖 <b>WB Analytics Pro Bot</b>\n\n"
            "Для начала работы отправьте /start\n"
            "Для нового расчета - /start\n\n"
            "<i>Бот анализирует отчеты Wildberries и рассчитывает "
            "ключевые финансовые показатели вашего бизнеса.</i>"
        )
