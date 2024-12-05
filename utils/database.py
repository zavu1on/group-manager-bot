import aiosqlite

from dto.birthday import CreateBirthdayDTO, BirthdayDTO
from dto.deadline import DeadlineDTO, CreateDeadlineDTO

try:
    from config import DB_PATH
except ModuleNotFoundError:
    raise ModuleNotFoundError("Add config file!")


async def create_tables() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                group_id INTEGER NOT NULL,
                date TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                group_id INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)
        await db.commit()


""" DEADLINES """


async def add_deadline(deadline: CreateDeadlineDTO) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO deadlines (task_name, group_id, date) VALUES (?, ?, ?)
        """, (deadline.task_name, deadline.group_id, deadline.date))
        await db.commit()


async def delete_deadline(deadline_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM deadlines WHERE id = ?
        """, (deadline_id,))
        await db.commit()


async def get_last_deadline(group_id: int) -> DeadlineDTO | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deadlines WHERE group_id = ? ORDER BY id DESC LIMIT 1", (group_id,)) as cursor:
            deadline = await cursor.fetchone()
            if deadline:
                return DeadlineDTO(**deadline)


async def get_deadlines_with_pagination(group_id: int, offset: int, limit: int = 5) -> list[DeadlineDTO]:
    response = []
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deadlines WHERE group_id = ? LIMIT ? OFFSET ?", (group_id, limit, offset)) as cursor:
            async for row in cursor:
                response.append(DeadlineDTO(**row))
    return response


async def get_all_deadlines() -> list[DeadlineDTO]:
    response = []
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deadlines") as cursor:
            async for row in cursor:
                response.append(DeadlineDTO(**row))
    return response


""" BIRTHDAYS """


async def add_birthday(birthday: CreateBirthdayDTO) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO birthdays (name, group_id, date) VALUES (?, ?, ?)
        """, (birthday.name, birthday.group_id, birthday.date))
        await db.commit()


async def delete_birthday(birthday_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM birthdays WHERE id = ?
        """, (birthday_id,))
        await db.commit()


async def get_last_birthday(group_id: int) -> BirthdayDTO | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM birthdays WHERE group_id = ? ORDER BY id DESC LIMIT 1", (group_id,)) as cursor:
            birthday = await cursor.fetchone()
            if birthday:
                return BirthdayDTO(**birthday)


async def get_birthdays_with_pagination(group_id: int, offset: int, limit: int = 5) -> list[BirthdayDTO]:
    response = []
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM birthdays WHERE group_id = ? LIMIT ? OFFSET ?", (group_id, limit, offset)) as cursor:
            async for row in cursor:
                response.append(BirthdayDTO(**row))
    return response


async def get_all_birthdays() -> list[BirthdayDTO]:
    response = []
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM birthdays") as cursor:
            async for row in cursor:
                response.append(BirthdayDTO(**row))
    return response
