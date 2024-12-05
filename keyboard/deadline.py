from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dto.deadline import DeadlineDTO


def create_remove_deadline_keyboard_builder(deadlines: list[DeadlineDTO], offset: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for idx, deadline in enumerate(deadlines):
        builder.row(InlineKeyboardButton(
            text=f"{offset + idx + 1}) {deadline.task_name} — {deadline.date}\n",
            callback_data=f"remove_deadline_{deadline.id}"
        ))
    return builder
