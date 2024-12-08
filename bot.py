import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, ChatAdministratorRights

from handlers import common, deadline, birthday
from utils.cron import daily_check_birthdays, daily_check_deadlines
from utils.database import create_tables

try:
    from config import BOT_TOKEN
except ModuleNotFoundError:
    raise ModuleNotFoundError("Add config file!")


async def main():
    logging.basicConfig(level=logging.ERROR)
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(common.common_router)
    dp.include_router(deadline.deadline_router)
    dp.include_router(birthday.birthday_router)

    await bot.set_my_default_administrator_rights(ChatAdministratorRights(
        can_manage_chat=True,
        can_delete_messages=False,
        can_manage_video_chats=False,
        can_restrict_members=False,
        can_promote_members=False,
        can_change_info=False,
        can_invite_users=False,
        can_edit_messages=False,
        can_edit_stories=False,
        can_manage_topics=False,
        can_pin_messages=False,
        can_post_messages=False,
        can_post_stories=False,
        can_delete_stories=False,
        is_anonymous=False,
    ))
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Получить помощь"),
        BotCommand(command="tarot", description="Получить карту Таро с предсказанием"),
        BotCommand(command="wander_ball", description="Получить ответ от шара судьбы"),
        BotCommand(command="chill_student", description="Какой ты сегодня студент"),
        BotCommand(command="joke", description="Расскажу анекдот"),
        BotCommand(command="joke_black", description="Расскажу анекдот, но также может быть черный юмор"),

        BotCommand(command="add_deadline", description="Добавить дедлайн"),
        BotCommand(command="view_deadlines", description="Посмотреть предстоящие дедлайны"),
        BotCommand(command="remove_deadline", description="Удалить дедлайн"),

        BotCommand(command="add_birthday", description="Добавить ДР"),
        BotCommand(command="view_birthdays", description="Посмотреть предстоящие дни рождения"),
        BotCommand(command="remove_birthday", description="Удалить ДР"),
    ])

    await create_tables()

    asyncio.create_task(daily_check_deadlines())
    asyncio.create_task(daily_check_birthdays())

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
