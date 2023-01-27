import asyncio
from collections.abc import Iterable
from typing import Any, LiteralString, Optional

import aiosqlite

from botanim_bot import config


async def get_db() -> aiosqlite.Connection:
    if not getattr(get_db, "db", None):
        db = await aiosqlite.connect(config.SQLITE_DB_FILE)
        get_db.db = db
    return get_db.db


async def fetch_all(sql: LiteralString, params: Optional[Iterable[Any]] = None):
    results = []
    db = await get_db()
    args: tuple[LiteralString, Optional[Iterable[Any]]] = (sql, params)
    cursor = await db.execute(*args)
    column_names = [d[0] for d in cursor.description]
    db.row_factory = aiosqlite.Row
    rows = await cursor.fetchall()
    for row_ in rows:
        row = {}
        for index, column_name in enumerate(column_names):
            row[column_name] = row_[index]
        results.append(row)
    await cursor.close()
    return results


async def fetch_one(sql: LiteralString, params: Optional[Iterable[Any]] = None):
    db = await get_db()
    args: tuple[LiteralString, Optional[Iterable[Any]]] = (sql, params)
    cursor = await db.execute(*args)
    column_names = [d[0] for d in cursor.description]
    db.row_factory = aiosqlite.Row
    row_ = await cursor.fetchone()
    if not row_:
        return None
    row = {}
    for index, column_name in enumerate(column_names):
        row[column_name] = row_[index]
    await cursor.close()
    return row


async def execute(sql: LiteralString, params: Optional[Iterable[Any]] = None):
    db = await get_db()
    args: tuple[LiteralString, Optional[Iterable[Any]]] = (sql, params)
    await db.execute(*args)
    await db.commit()


async def _async_close_db():
    await (await get_db()).close()


def close_db():
    asyncio.run(_async_close_db())
