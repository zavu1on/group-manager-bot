import asyncio
import datetime
from random import choice

from aiogram.client.session import aiohttp
from config import BOT_TOKEN
from utils.database import get_all_birthdays, get_all_deadlines, delete_deadline
from assets.text import *


async def send_message(chat_id: int, text: str):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'html',
            })
    except Exception:
        pass


BIRTHDAY_NOTIFY_PERIODS = [
    (datetime.timedelta(days=31), MONTH_BEFORE_THE_BIRTHDAY),
    (datetime.timedelta(days=7), SEVEN_DAYS_BEFORE_THE_BIRTHDAY),
    (datetime.timedelta(days=1), ONE_DAY_BEFORE_THE_BIRTHDAY),
]
DEADLINE_NOTIFY_PERIODS = [
    (datetime.timedelta(days=3), THREE_DAYS_BEFORE_THE_DEADLINE),
    (datetime.timedelta(days=1), ONE_DAY_BEFORE_THE_DEADLINE),
]


async def daily_check_birthdays():
    while True:
        birthdays = await get_all_birthdays()
        for birthday in birthdays:
            bday = datetime.datetime.strptime(birthday.date, "%d.%m.%Y")
            today = datetime.datetime.today()

            for delta, func in BIRTHDAY_NOTIFY_PERIODS:
                computed = today + delta
                if bday.day == computed.day and bday.month == computed.month:
                    await send_message(birthday.group_id, func(birthday.name))
            if bday.day == today.day and bday.month == today.month:
                congrats = choice(CRINGE_CONGRATS)
                await send_message(birthday.group_id, f"Сегодня у <i>{birthday.name}</i> день рождения 🥳❤️\n{congrats}")

        await asyncio.sleep(60 * 60 * 24)


async def daily_check_deadlines():
    while True:
        deadlines = await get_all_deadlines()
        for deadline in deadlines:
            date = datetime.datetime.strptime(deadline.date, "%d.%m.%Y")
            today = datetime.datetime.today()

            for delta, func in DEADLINE_NOTIFY_PERIODS:
                computed = today + delta
                if date.date() == computed.date():
                    await send_message(deadline.group_id, func(deadline.task_name))
            if date.date() == today.date():
                await delete_deadline(deadline.id)
                await send_message(deadline.group_id, FINISH_DEADLINE(deadline.task_name))

        await asyncio.sleep(60 * 60 * 24)
