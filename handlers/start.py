from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.dispatcher import dp
from services.session_manager import session_manager
from keyboards.factories import KeyboardFactory
from states.analytics import AnalyticsState
from services.referral_manager import referral_manager


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Регистрируем реферала, если бот запущен по реферальной ссылке с параметром
    if message.text:
        parts = message.text.split()
        if len(parts) > 1 and parts[1].startswith("ref_"):
            try:
                referrer_id = int(parts[1].split("_", 1)[1])
            except ValueError:
                referrer_id = None
            if referrer_id and referrer_id != message.from_user.id:
                added = referral_manager.register_referral(
                    referrer_id, message.from_user.id
                )
                if added:
                    await message.answer(
                        "📎 Вы пришли по реферальной ссылке!\n"
                        "Рефереру будет начислен бонус, когда вы активируете аккаунт 💪"
                    )

    session = session_manager.get_session(message.from_user.id)
    session.update_activity()

    await state.set_state(AnalyticsState.waiting_for_tax)
    await message.answer(
        "👋 Добро пожаловать в WB Analytics Pro!\n"
        "Я помогу вам проанализировать эффективность вашего бизнеса на Wildberries.\n\n"
        "📊 <b>Выберите налоговую ставку:</b>",
        reply_markup=KeyboardFactory.get_tax_keyboard(),
    )
