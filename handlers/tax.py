from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.dispatcher import dp
from services.session_manager import session_manager
from keyboards.factories import KeyboardFactory
from states.analytics import AnalyticsState


@dp.callback_query(F.data.startswith("tax_"))
async def process_tax_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора налоговой ставки"""
    session = session_manager.get_session(callback.from_user.id)

    if callback.data == "tax_other":
        await state.set_state(AnalyticsState.waiting_for_tax)
        await callback.message.edit_text(
            "💵 <b>Введите вашу налоговую ставку в процентах:</b>\n"
            "Например: <code>5.5</code> или <code>6</code>"
        )
    else:
        tax_rate = float(callback.data.split("_")[1])
        session.tax_rate = tax_rate
        await state.set_state(AnalyticsState.waiting_for_main_file)
        await callback.message.edit_text(
            f"✅ <b>Налоговая ставка:</b> {tax_rate}%\n\n"
            "📁 <b>Теперь отправьте основной отчет из личного кабинета Wildberries:</b>\n"
            "• Это должен быть Excel-файл с данными о продажах\n"
            "• Максимальный размер: 10MB",
            reply_markup=None,
        )

    await callback.answer()


@dp.message(AnalyticsState.waiting_for_tax)
async def process_custom_tax(message: Message, state: FSMContext):
    """Обработчик пользовательской налоговой ставки"""
    session = session_manager.get_session(message.from_user.id)

    try:
        tax_rate = float(message.text.replace(",", "."))
        if tax_rate <= 0 or tax_rate >= 100:
            raise ValueError

        session.tax_rate = tax_rate
        await state.set_state(AnalyticsState.waiting_for_main_file)
        await message.answer(
            f"✅ <b>Налоговая ставка установлена:</b> {tax_rate}%\n\n"
            "📁 <b>Теперь отправьте основной отчет из личного кабинета Wildberries:</b>",
            reply_markup=None,
        )

    except ValueError:
        await message.answer(
            "❌ <b>Неверный формат!</b>\n"
            "Введите число от 0 до 100, например: <code>6.5</code>"
        )
