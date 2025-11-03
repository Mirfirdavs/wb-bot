from aiogram.filters import Command
from aiogram.types import Message
from bot.dispatcher import dp
from bot.bot import bot
from config import Config
from services.referral_manager import referral_manager

# Кэш для username бота, чтобы формировать ссылку без повторных запросов get_me
_bot_username: str = None


@dp.message(Command("ref"))
async def cmd_ref(message: Message):
    """Команда /ref – показать реферальную информацию пользователя."""
    global _bot_username
    user_id = message.from_user.id
    # Получаем статистику пользователя: всего приглашено, активных, бонусов
    total, active, bonus = referral_manager.get_stats(user_id)

    # Получаем username бота для формирования ссылки
    if _bot_username is None:
        bot_info = await bot.get_me()
        _bot_username = bot_info.username or "bot"
    ref_link = f"https://t.me/{_bot_username}?start=ref_{user_id}"

    await message.answer(
        "👥 <b>Реферальная программа</b>\n\n"
        f"🔗 Ваша ссылка: {ref_link}\n"
        f"👤 Приглашено всего: <b>{total}</b>\n"
        f"✅ Активных: <b>{active}</b>\n"
        f"💰 Начислено бонусов: <b>{bonus}</b>"
    )


@dp.message(Command("activate_me"))
async def cmd_activate_me(message: Message):
    """Команда /activate_me – активировать аккаунт и начислить бонус рефереру."""
    user_id = message.from_user.id
    info = referral_manager.referrals.get(user_id)

    if not info:
        await message.answer("ℹ️ У вас нет реферера.")
        return

    if info.get("activated"):
        await message.answer("⚠️ Ваш аккаунт уже активирован.")
        return

    referral_manager.activate_referral(user_id)
    await message.answer("✅ Ваш аккаунт активирован! Ваш реферер получил бонус.")


@dp.message(Command("reset_referrals"))
async def cmd_reset_referrals(message: Message):
    """Команда /reset_referrals – сброс начислений (доступ только администраторам)."""
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("⛔ У вас нет прав доступа.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Укажите ID пользователя.")
        return

    try:
        referrer_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный формат ID.")
        return

    total, active, bonus = referral_manager.get_stats(referrer_id)
    if total == 0 and active == 0 and bonus == 0:
        await message.answer("ℹ️ У пользователя нет данных для сброса.")
        return

    referral_manager.reset_referrals(referrer_id)
    await message.answer(f"✅ Начисления пользователя {referrer_id} сброшены.")
