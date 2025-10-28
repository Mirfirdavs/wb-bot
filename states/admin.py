from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    """Состояния FSM для админки"""

    waiting_broadcast_message = State()
    waiting_export_type = State()
    waiting_user_action = State()
