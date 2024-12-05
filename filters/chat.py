from aiogram.enums import ChatType
from aiogram.types import Message


def is_private_chat(message: Message) -> bool:
    return message.chat.type == ChatType.PRIVATE


def is_group_chat(message: Message) -> bool:
    return message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}
