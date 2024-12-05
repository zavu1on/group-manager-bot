from aiogram.fsm.state import StatesGroup, State


class AddDeadlineForm(StatesGroup):
    task_name = State()
    date = State()
