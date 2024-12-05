from enum import Enum

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_pagination_keyboard_builder(offset: int, limit: int, paginate_prefix: str, show_last: bool = True, inherited_keyboard: InlineKeyboardBuilder = None) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    was_edit = False
    if inherited_keyboard:
        builder = inherited_keyboard

    if offset >= limit:
        builder.row(InlineKeyboardButton(
            text="<<",
            callback_data=f"{paginate_prefix}_{offset - limit}_{limit}",
        ))
        was_edit = True
    if limit != 0 and show_last:
        func = builder.add if was_edit else builder.row
        func(InlineKeyboardButton(
            text=">>",
            callback_data=f"{paginate_prefix}_{offset + limit}_{limit}",
        ))

    return builder


class PaginationMessageModeEnum(Enum):
    REPLY = "reply"
    EDIT = "EDIT"
