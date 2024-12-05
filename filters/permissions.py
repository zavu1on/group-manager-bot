from aiogram.types import Message
from aiogram.utils.chat_member import ADMINS


async def is_admin(message: Message, user_id: int) -> bool:
    member = await message.bot.get_chat_member(message.chat.id, user_id)
    return isinstance(member, ADMINS)