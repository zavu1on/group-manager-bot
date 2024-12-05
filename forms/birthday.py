from aiogram.fsm.state import StatesGroup, State


class AddBirthdayForm(StatesGroup):
    name = State()
    date = State()
