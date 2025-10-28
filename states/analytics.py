from aiogram.fsm.state import State, StatesGroup


class AnalyticsState(StatesGroup):
    """Состояния FSM для процесса аналитики"""

    waiting_for_tax = State()
    waiting_for_main_file = State()
    waiting_for_cost_file = State()
    ready_for_analysis = State()
