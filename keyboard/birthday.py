from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dto.birthday import BirthdayDTO


def create_remove_birthday_keyboard_builder(birthdays: list[BirthdayDTO], offset: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for idx, deadline in enumerate(birthdays):
        builder.row(InlineKeyboardButton(
            text=f"{offset + idx + 1}) {deadline.name} — {deadline.date}\n",
            callback_data=f"remove_birthday_{deadline.id}"
        ))
    return builder
