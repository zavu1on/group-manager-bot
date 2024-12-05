import datetime

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from dto.birthday import CreateBirthdayDTO
from filters.chat import is_group_chat
from filters.permissions import is_admin
from forms.birthday import AddBirthdayForm
from assets.text import *
from keyboard.birthday import create_remove_birthday_keyboard_builder
from keyboard.pagination import PaginationMessageModeEnum, create_pagination_keyboard_builder
from utils.database import get_birthdays_with_pagination, get_last_birthday, delete_birthday, add_birthday

birthday_router = Router()


@birthday_router.message(Command("add_birthday"), is_group_chat)
async def add_birthday_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message, message.bot.id):
        await message.reply(NOT_ADMIM)
        return

    await message.reply(ADD_BIRTHDAY)
    await state.set_state(AddBirthdayForm.name)


@birthday_router.message(AddBirthdayForm.name)
async def process_birthday_cmd(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply(PROCCESS_BIRTHDAY(message.text), parse_mode='html')

    await state.set_state(AddBirthdayForm.date)


@birthday_router.message(AddBirthdayForm.date)
async def process_date_cmd(message: types.Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.reply(DEADLINE_PARSE_ERROR)
        return


    await state.update_data(date=date)
    data = await state.get_data()
    birthday_dto = CreateBirthdayDTO(data['name'], message.chat.id, message.text)
    await add_birthday(birthday_dto)

    await message.reply(BIRTHDAY_ADD_SUCCESS, parse_mode="html")
    await state.clear()


async def view_birthdays_handler(message: types.Message, offset: int, limit: int, mode: PaginationMessageModeEnum):
    birthdays = await get_birthdays_with_pagination(message.chat.id, offset, limit)
    last_birthday = await get_last_birthday(message.chat.id)
    data = ""
    show_last = True

    if not birthdays:
        return await message.reply('Тут пока ничего нет 👽')

    if birthdays[-1].id == last_birthday.id:
        show_last = False

    keyboard = create_pagination_keyboard_builder(
        offset,
        limit,
        "paginate_view_birthdays",
        show_last
    ).as_markup()

    for idx, birthday in enumerate(birthdays):
        data += f"{offset + idx + 1}) <b>{birthday.name}</b> — {birthday.date}\n"

    func = message.reply if mode == PaginationMessageModeEnum.REPLY else message.edit_text
    await func("Вот все днюхи 🥰\n\n" + data, parse_mode="html", reply_markup=keyboard)


@birthday_router.message(Command("view_birthdays"), is_group_chat)
async def view_birthdays_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    return await view_birthdays_handler(message, 0, 5, PaginationMessageModeEnum.REPLY)


@birthday_router.callback_query(lambda call: call.data.startswith("paginate_view_birthdays"))
async def view_birthdays_callback_handler(callback: types.CallbackQuery):
    _, offset, limit = callback.data.split("paginate_view_birthdays")[1].split('_')
    return await view_birthdays_handler(callback.message, int(offset), int(limit), PaginationMessageModeEnum.EDIT)


async def remove_birthday_handler(message: types.Message, offset: int, limit: int, mode: PaginationMessageModeEnum):
    birthdays = await get_birthdays_with_pagination(message.chat.id, offset, limit)
    last_birthday = await get_last_birthday(message.chat.id)
    show_last = True

    if not birthdays:
        return await message.reply('Тут пока ничего нет 🙉')

    if birthdays[-1].id == last_birthday.id:
        show_last = False

    remove_keyboard = create_remove_birthday_keyboard_builder(birthdays, offset)
    pagination_keyboard = create_pagination_keyboard_builder(
        offset,
        limit,
        "paginate_remove_birthday",
        show_last,
        inherited_keyboard=remove_keyboard,
    ).as_markup()

    func = message.reply if mode == PaginationMessageModeEnum.REPLY else message.edit_text
    await func("Выбери дни рождения, который нужно удалить 😔", reply_markup=pagination_keyboard)


@birthday_router.message(Command("remove_birthday"), is_group_chat)
async def remove_birthday_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    return await remove_birthday_handler(message, 0, 5, PaginationMessageModeEnum.REPLY)


@birthday_router.callback_query(lambda call: call.data.startswith("paginate_remove_birthday"))
async def remove_birthday_callback_handler(callback: types.CallbackQuery):
    _, offset, limit = callback.data.split("paginate_remove_birthday")[1].split('_')
    return await remove_birthday_handler(callback.message, int(offset), int(limit), PaginationMessageModeEnum.EDIT)


@birthday_router.callback_query(lambda call: call.data.startswith("remove_birthday_"))
async def remove_birthday_callback_handler(callback: types.CallbackQuery):
    _, id_ = callback.data.split("remove_birthday_")


    await delete_birthday(int(id_))
    await callback.message.edit_text("День рождения успешно удален 🥶")
