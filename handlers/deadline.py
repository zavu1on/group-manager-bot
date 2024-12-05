import datetime

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from dto.deadline import CreateDeadlineDTO
from filters.chat import is_group_chat
from filters.permissions import is_admin
from forms.deadline import AddDeadlineForm
from assets.text import *
from keyboard.deadline import create_remove_deadline_keyboard_builder
from keyboard.pagination import PaginationMessageModeEnum, create_pagination_keyboard_builder
from utils.database import add_deadline, get_deadlines_with_pagination, get_last_deadline, delete_deadline

deadline_router = Router()


@deadline_router.message(Command("add_deadline"), is_group_chat)
async def add_deadline_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message, message.bot.id):
        await message.reply(NOT_ADMIM)
        return

    await message.reply("Давай добавим новый дедлайн 🔥\nНапиши, что нужно сделать?")
    await state.set_state(AddDeadlineForm.task_name)


@deadline_router.message(AddDeadlineForm.task_name)
async def process_deadline_cmd(message: types.Message, state: FSMContext):
    await state.update_data(task_name=message.text)
    await message.reply(PROCCESS_DEADLINE(message.text), parse_mode='html')

    await state.set_state(AddDeadlineForm.date)


@deadline_router.message(AddDeadlineForm.date)
async def process_date_cmd(message: types.Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.reply(DEADLINE_PARSE_ERROR)
        return
    if date < datetime.datetime.today():
        await message.reply(DEADLINE_INVALID_DATE)
        return


    await state.update_data(date=date)
    data = await state.get_data()
    deadline_dto = CreateDeadlineDTO(data['task_name'], message.chat.id, message.text)
    await add_deadline(deadline_dto)

    await message.reply(DEADLINE_ADD_SUCCESS, parse_mode="html")
    await state.clear()


async def view_deadlines_handler(message: types.Message, offset: int, limit: int, mode: PaginationMessageModeEnum):
    deadlines = await get_deadlines_with_pagination(message.chat.id, offset, limit)
    last_deadline = await get_last_deadline(message.chat.id)
    data = ""
    show_last = True

    if not deadlines:
        await message.reply('Тут пока ничего нет 🙈')
        return

    if deadlines[-1].id == last_deadline.id:
        show_last = False

    keyboard = create_pagination_keyboard_builder(
        offset,
        limit,
        "paginate_view_deadlines",
        show_last
    ).as_markup()

    for idx, deadline in enumerate(deadlines):
        data += f"{offset + idx + 1}) <b>{deadline.task_name}</b> — {deadline.date}\n"

    func = message.reply if mode == PaginationMessageModeEnum.REPLY else message.edit_text
    await func("Вот предстоящие дедлайны 👇\n\n" + data, parse_mode="html", reply_markup=keyboard)


@deadline_router.message(Command("view_deadlines"), is_group_chat)
async def view_deadlines_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    return await view_deadlines_handler(message, 0, 5, PaginationMessageModeEnum.REPLY)


@deadline_router.callback_query(lambda call: call.data.startswith("paginate_view_deadlines"))
async def view_deadlines_callback_handler(callback: types.CallbackQuery):
    _, offset, limit = callback.data.split("paginate_view_deadlines")[1].split('_')
    return await view_deadlines_handler(callback.message, int(offset), int(limit), PaginationMessageModeEnum.EDIT)


async def remove_deadline_handler(message: types.Message, offset: int, limit: int, mode: PaginationMessageModeEnum):
    deadlines = await get_deadlines_with_pagination(message.chat.id, offset, limit)
    last_deadline = await get_last_deadline(message.chat.id)
    show_last = True

    if not deadlines:
        await message.reply('Тут пока ничего нет 🙉')
        return

    if deadlines[-1].id == last_deadline.id:
        show_last = False

    remove_keyboard = create_remove_deadline_keyboard_builder(deadlines, offset)
    pagination_keyboard = create_pagination_keyboard_builder(
        offset,
        limit,
        "paginate_remove_deadline",
        show_last,
        inherited_keyboard=remove_keyboard,
    ).as_markup()

    func = message.reply if mode == PaginationMessageModeEnum.REPLY else message.edit_text
    await func("Выбери дедлайн, который нужно удалить ❌", reply_markup=pagination_keyboard)


@deadline_router.message(Command("remove_deadline"), is_group_chat)
async def remove_deadline_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    return await remove_deadline_handler(message, 0, 5, PaginationMessageModeEnum.REPLY)


@deadline_router.callback_query(lambda call: call.data.startswith("paginate_remove_deadline"))
async def remove_deadline_callback_handler(callback: types.CallbackQuery):
    _, offset, limit = callback.data.split("paginate_remove_deadline")[1].split('_')
    return await remove_deadline_handler(callback.message, int(offset), int(limit), PaginationMessageModeEnum.EDIT)


@deadline_router.callback_query(lambda call: call.data.startswith("remove_deadline_"))
async def remove_deadline_callback_handler(callback: types.CallbackQuery):
    _, id_ = callback.data.split("remove_deadline_")

    await delete_deadline(int(id_))
    await callback.message.edit_text("Дедлайн успешно удален 🤐")
