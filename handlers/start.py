from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.dispatcher import dp
from services.session_manager import session_manager
from keyboards.factories import KeyboardFactory
from states.analytics import AnalyticsState


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    session = session_manager.get_session(message.from_user.id)
    session.update_activity()

    await state.set_state(AnalyticsState.waiting_for_tax)
    await message.answer(
        "👋 Добро пожаловать в WB Analytics Pro!\n"
        "Я помогу вам проанализировать эффективность вашего бизнеса на Wildberries.\n\n"
        "📊 <b>Выберите налоговую ставку:</b>",
        reply_markup=KeyboardFactory.get_tax_keyboard(),
    )
