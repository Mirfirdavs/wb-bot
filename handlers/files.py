import asyncio
import async_timeout
from io import BytesIO

from aiogram import F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot.dispatcher import dp
from bot.bot import bot
from services.session_manager import session_manager
from services.validators import FileValidator
from services.data_processor import DataProcessor
from keyboards.factories import KeyboardFactory
from states.analytics import AnalyticsState
from config import Config
from utils.logger import logger


@dp.message(AnalyticsState.waiting_for_main_file, F.document)
async def process_main_file(message: Message, state: FSMContext):
    """Обработка основного файла отчета"""
    session = session_manager.get_session(message.from_user.id)

    # Валидация файла
    if not FileValidator.validate_file_size(message):
        await message.answer(
            "❌ <b>Файл слишком большой!</b>\n"
            f"Максимальный размер: {Config.MAX_FILE_SIZE // 1024 // 1024}MB"
        )
        return

    if not FileValidator.validate_file_type(message):
        await message.answer(
            "❌ <b>Неверный формат файла!</b>\n"
            "Пожалуйста, отправьте файл в формате Excel (.xlsx или .xls)"
        )
        return

    try:
        # Скачивание и обработка файла
        doc = message.document
        file = await bot.get_file(doc.file_id)

        async with async_timeout.timeout(Config.PROCESSING_TIMEOUT):
            file_bytes = BytesIO()
            await bot.download_file(file.file_path, destination=file_bytes)
            file_bytes.seek(0)

            # Обработка данных
            processing_msg = await message.answer(
                "⏳ <b>Обрабатываю основной отчет...</b>"
            )

            session.main_df = DataProcessor.process_main_report(file_bytes)
            session.update_activity()

            await processing_msg.edit_text(
                "✅ <b>Основной отчет успешно обработан!</b>\n\n"
                "📊 <b>Теперь отправьте файл с себестоимостью:</b>\n"
                "• Excel-файл с колонками: <code>Артикул поставщика, Себестоимость</code>\n"
                "• Максимальный размер: 10MB"
            )

            await state.set_state(AnalyticsState.waiting_for_cost_file)

    except asyncio.TimeoutError:
        await message.answer(
            "❌ <b>Превышено время обработки!</b>\n"
            "Файл слишком большой или сложный. Попробуйте разбить данные на части."
        )
    except Exception as e:
        logger.error(f"Error processing main file: {e}")
        await message.answer(
            f"❌ <b>Ошибка обработки файла:</b>\n<code>{str(e)}</code>\n\n"
            "Проверьте, что файл соответствует формату отчетов Wildberries."
        )


@dp.message(AnalyticsState.waiting_for_cost_file, F.document)
async def process_cost_file(message: Message, state: FSMContext):
    """Обработка файла себестоимости"""
    session = session_manager.get_session(message.from_user.id)

    if session.main_df is None:
        await message.answer("⚠️ Сначала отправьте основной отчет!")
        return

    # Валидация файла
    if not FileValidator.validate_file_size(message):
        await message.answer("❌ Файл слишком большой!")
        return

    if not FileValidator.validate_file_type(message):
        await message.answer("❌ Неверный формат файла!")
        return

    try:
        # Скачивание файла
        doc = message.document
        file = await bot.get_file(doc.file_id)

        async with async_timeout.timeout(Config.PROCESSING_TIMEOUT):
            file_bytes = BytesIO()
            await bot.download_file(file.file_path, destination=file_bytes)
            file_bytes.seek(0)

            # Обработка данных
            processing_msg = await message.answer(
                "⏳ <b>Рассчитываю финансовые показатели...</b>"
            )

            session.final_df = DataProcessor.process_cost_data(
                file_bytes, session.main_df, session.tax_rate
            )
            session.update_activity()

            await processing_msg.edit_text(
                "✅ <b>Финансовый анализ завершен!</b>\n\n📈 <b>Доступные отчеты:</b>",
                reply_markup=KeyboardFactory.get_analysis_keyboard(),
            )

            await state.set_state(AnalyticsState.ready_for_analysis)

    except asyncio.TimeoutError:
        await message.answer("❌ Превышено время обработки!")
    except Exception as e:
        logger.error(f"Error processing cost file: {e}")
        await message.answer(
            f"❌ Ошибка обработки файла себестоимости:\n<code>{str(e)}</code>"
        )
