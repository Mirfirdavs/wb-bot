from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.dispatcher import dp
from services.payment_service import PaymentService
from services.transaction_storage import save_transaction

# 💳 FSM для произвольного доната
class DonateState(StatesGroup):
    waiting_for_custom_amount = State()


# 📌 Обработчик команды /donate
@dp.message(Command("donate"))
async def donate_command(message: Message):
    kb = InlineKeyboardBuilder()
    for amount in [100, 300, 500]:
        kb.button(text=f"{amount} ₽", callback_data=f"donate_{amount}")
    kb.button(text="Другая сумма", callback_data="donate_custom")
    await message.answer(
        "💸 Выберите сумму для поддержки проекта:", reply_markup=kb.as_markup()
    )


# 📌 Обработка фиксированных сумм
@dp.callback_query(lambda c: c.data and c.data.startswith("donate_"))
async def donate_callback(callback: CallbackQuery):
    data = callback.data
    if data == "donate_custom":
        await callback.message.answer("✍️ Введите сумму, которую хотите отправить:")
        await DonateState.waiting_for_custom_amount.set()
    else:
        amount = int(data.split("_")[1])
        url = PaymentService.create_payment_link(callback.from_user.id, amount)
        await callback.message.answer(
            f"🔗 Перейдите по ссылке для оплаты: {url}\n\n"
            "После оплаты вы получите благодарность!"
        )
        await callback.answer()


# 📌 Обработка ввода произвольной суммы
@dp.message(DonateState.waiting_for_custom_amount)
async def handle_custom_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount < 10:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректную сумму (число от 10 ₽).")
        return

    url = PaymentService.create_payment_link(message.from_user.id, amount)
    await message.answer(f"🔗 Ваша ссылка на оплату: {url}\n\nСпасибо за поддержку! ❤️")
    await state.clear()
