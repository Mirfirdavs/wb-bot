from aiogram import F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime

from bot.dispatcher import dp
from bot.bot import bot
from config import Config
from services.admin_manager import admin_manager
from services.admin_reporter import AdminReporter
from services.session_manager import session_manager
from states.admin import AdminState
from keyboards.admin import AdminKeyboard
from utils.logger import logger

def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    return user_id in Config.ADMIN_IDS

# ===== ОСНОВНЫЕ КОМАНДЫ =====

@dp.message(Command("admin"), F.chat.type == 'private')
async def cmd_admin(message: Message, state: FSMContext):
    """Команда админ-панели"""
    await state.clear()  # опционально: сбросить состояние
    
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав доступа к админ-панели.")
        return
    
    # Обновляем статистику активности админа
    admin_manager.update_user_activity(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    
    await message.answer(
        "🛠 <b>Админ-панель WB Analytics</b>\n\n"
        "Выберите действие:",
        reply_markup=AdminKeyboard.get_admin_main()
    )

@dp.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Возврат в главное меню админки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    await callback.message.edit_text(
        "🛠 <b>Админ-панель WB Analytics</b>\n\n"
        "Выберите действие:",
        reply_markup=AdminKeyboard.get_admin_main()
    )

# ===== СТАТИСТИКА =====

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Показать статистику"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    try:
        stats_message = AdminReporter.format_stats_message()
        await callback.message.edit_text(
            stats_message,
            reply_markup=AdminKeyboard.get_stats_refresh()
        )
    except Exception as e:
        logger.error(f"Error generating stats: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка получения статистики: {str(e)}",
            reply_markup=AdminKeyboard.get_back_button()
        )

@dp.callback_query(F.data == "admin_detailed_stats")
async def admin_detailed_stats(callback: CallbackQuery):
    """Детальная статистика"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    try:
        df = admin_manager.get_user_stats_df()
        if df.empty:
            await callback.message.edit_text(
                "📊 Нет данных о пользователях",
                reply_markup=AdminKeyboard.get_back_button()
            )
            return
        
        # Топ 10 пользователей
        top_users = df.nlargest(10, 'files_processed')
        message_lines = ["🏆 <b>ТОП-10 пользователей по активности:</b>\n"]
        
        for idx, (_, user) in enumerate(top_users.iterrows(), 1):
            username = user['username'] if user['username'] != "Нет" else "без username"
            message_lines.append(
                f"{idx}. ID: {user['user_id']} ({username}) - "
                f"{user['files_processed']} файлов, {user['sessions']} сессий"
            )
        
        await callback.message.edit_text(
            "\n".join(message_lines),
            reply_markup=AdminKeyboard.get_stats_refresh()
        )
        
    except Exception as e:
        logger.error(f"Error generating detailed stats: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}",
            reply_markup=AdminKeyboard.get_back_button()
        )

# ===== ЭКСПОРТ ДАННЫХ =====

@dp.callback_query(F.data == "admin_export")
async def admin_export(callback: CallbackQuery):
    """Меню экспорта данных"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    await callback.message.edit_text(
        "📁 <b>Экспорт данных</b>\n\n"
        "Выберите формат экспорта:",
        reply_markup=AdminKeyboard.get_export_options()
    )

@dp.callback_query(F.data.startswith("export_"))
async def handle_export(callback: CallbackQuery):
    """Обработка экспорта данных"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    export_type = callback.data.split("_")[1]
    
    try:
        processing_msg = await callback.message.answer("⏳ <b>Генерирую отчет...</b>")
        
        if export_type == "excel":
            excel_file = AdminReporter.generate_users_excel()
            file = BufferedInputFile(
                excel_file.getvalue(),
                filename=f"wb_bot_stats_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            )
            caption = "📊 <b>Полная статистика бота в Excel</b>"
            await callback.message.answer_document(file, caption=caption)
            
        elif export_type == "charts":
            chart_file = AdminReporter.generate_activity_chart()
            file = BufferedInputFile(
                chart_file.getvalue(),
                filename=f"wb_activity_chart_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            )
            caption = "📈 <b>Графики активности пользователей</b>"
            await callback.message.answer_photo(file, caption=caption)
        
        await processing_msg.delete()
        await callback.answer("✅ Отчет готов!")
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка при экспорте: {str(e)}",
            reply_markup=AdminKeyboard.get_back_button()
        )

# ===== РАССЫЛКА =====

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Начало рассылки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    await state.set_state(AdminState.waiting_broadcast_message)
    await callback.message.edit_text(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Отправьте сообщение для рассылки всем пользователям:",
        reply_markup=AdminKeyboard.get_back_button()
    )

@dp.message(AdminState.waiting_broadcast_message)
async def admin_broadcast_receive(message: Message, state: FSMContext):
    """Получение сообщения для рассылки"""
    if not is_admin(message.from_user.id):
        return
    
    broadcast_text = message.text
    total_users = len(admin_manager.user_stats)
    
    await state.update_data(broadcast_text=broadcast_text)
    await message.answer(
        f"📢 <b>Подтверждение рассылки</b>\n\n"
        f"<b>Сообщение:</b>\n{broadcast_text}\n\n"
        f"<b>Будет отправлено:</b> {total_users} пользователям\n\n"
        f"<i>Подтвердите отправку:</i>",
        reply_markup=AdminKeyboard.get_broadcast_confirm()
    )

@dp.callback_query(F.data == "broadcast_confirm")
async def admin_broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждение рассылки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    data = await state.get_data()
    broadcast_text = data.get('broadcast_text')
    
    if not broadcast_text:
        await callback.answer("❌ Сообщение не найдено")
        return
    
    # Отправляем рассылку
    progress_msg = await callback.message.answer("⏳ <b>Начинаю рассылку...</b>")
    
    try:
        result = await admin_manager.send_broadcast_message(
            bot, 
            broadcast_text,
            exclude_users=Config.ADMIN_IDS  # Не рассылаем админам
        )
        
        # Формируем отчет
        report_message = (
            f"📊 <b>Результаты рассылки</b>\n\n"
            f"✅ Успешно: {result['successful']}\n"
            f"❌ Не удалось: {result['failed']}\n"
            f"👥 Всего пользователей: {result['total']}\n"
        )
        
        if result['errors']:
            report_message += f"\n<code>Ошибки: {', '.join(result['errors'])}</code>"
        
        await progress_msg.edit_text(report_message)
        await callback.message.edit_text(
            "✅ <b>Рассылка завершена!</b>",
            reply_markup=AdminKeyboard.get_back_button()
        )
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await progress_msg.edit_text(f"❌ Ошибка рассылки: {str(e)}")
    
    await state.clear()

# ===== ПОЛЬЗОВАТЕЛИ =====

@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Управление пользователями"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    df = admin_manager.get_user_stats_df()
    
    if df.empty:
        await callback.message.edit_text(
            "👥 <b>Нет данных о пользователях</b>",
            reply_markup=AdminKeyboard.get_back_button()
        )
        return
    
    active_today = len(df[df['days_since_active'] == 0])
    new_today = len(df[df['days_since_active'].isna() | (df['days_since_active'] == 0)])
    
    message = (
        f"👥 <b>Управление пользователями</b>\n\n"
        f"📊 Всего пользователей: {len(df)}\n"
        f"🟢 Активных сегодня: {active_today}\n"
        f"🆕 Новых сегодня: {new_today}\n"
        f"📁 Среднее файлов на пользователя: {df['files_processed'].mean():.1f}\n\n"
        f"<i>Используйте экспорт для детальной информации</i>"
    )
    
    await callback.message.edit_text(
        message,
        reply_markup=AdminKeyboard.get_stats_refresh()
    )

# ===== ОБНОВЛЕНИЕ =====

@dp.callback_query(F.data == "admin_refresh")
async def admin_refresh(callback: CallbackQuery):
    """Обновление админ-панели"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    await admin_stats(callback)

# ===== ЗАКРЫТИЕ =====

@dp.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    """Закрытие админ-панели"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    await callback.message.delete()
    await callback.answer("Админ-панель закрыта")