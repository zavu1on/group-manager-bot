import aiohttp

from random import choice
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from filters.chat import is_private_chat, is_group_chat
from utils.localize import translate
from assets.text import *

common_router = Router()


@common_router.message(Command("start"), is_private_chat)
async def start_from_chat(message: types.Message, state: FSMContext):
    await message.reply(START_FROM_CHAT)
    await state.clear()


@common_router.message(Command("start"), is_group_chat)
async def start_from_group(message: types.Message, state: FSMContext):
    await message.reply(START_FROM_GROUP)
    await state.clear()


@common_router.message(Command("tarot"))
async def send_taro(message: types.Message, state: FSMContext):
    await state.clear()
    new_message = await message.reply(TAROT_PENDING)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://tarotapi.dev/api/v1/cards/random?n=1") as response:
                if response.ok:
                    data = await response.json()
                    data = data["cards"][0]

                    name = translate(data["name"])
                    meaning = translate(data["meaning_up"])

                    text = f"<b>{name}</b>\n{meaning}"
                    await new_message.edit_text(TAROT_SUCCESS + '\n\n' + text, parse_mode="html")
    except Exception:
        await new_message.edit_text(TAROT_FAIL)


@common_router.message(Command("wander_ball"))
async def send_wander_ball_advice(message: types.Message, state: FSMContext):
    response = choice(FORTUNE_RESPONSES)
    await message.reply(f"Шар говорит тебе:\n<i>{response}</i>🔮🌟", parse_mode="html")
    await state.clear()


@common_router.message(Command("chill_student"))
async def send_student_status(message: types.Message, state: FSMContext):
    status = choice(STUDENT_STATUSES)
    sticker_id = choice(CHILL_GUY_STICKERS)

    await message.reply(f"Оп-оп, сегодня ты 🤯\n<i>{status}</i>", parse_mode="html")
    await message.answer_sticker(sticker_id)
    await state.clear()


@common_router.message(Command("help"))
async def send_help_text(message: types.Message, state: FSMContext):
    await message.reply(HELP_TEXT)
    await state.clear()
