import asyncio
from collections.abc import Iterable
from typing import Any, LiteralString

import aiosqlite

from app import config


async def get_db() -> aiosqlite.Connection:
    if not getattr(get_db, "db", None):
        db = await aiosqlite.connect(config.SQLITE_DB_FILE)
        setattr(get_db, "db", db)

    return getattr(get_db, "db")


async def fetch_all(
    sql: LiteralString, params: Iterable[Any] | None = None
) -> list[dict]:
    cursor = await _get_cursor(sql, params)
    rows = await cursor.fetchall()
    results = []
    for row_ in rows:
        results.append(_get_result_with_column_names(cursor, row_))
    await cursor.close()
    return results


async def fetch_one(
    sql: LiteralString, params: Iterable[Any] | None = None
) -> dict | None:
    cursor = await _get_cursor(sql, params)
    row_ = await cursor.fetchone()
    if not row_:
        return None
    row = _get_result_with_column_names(cursor, row_)
    await cursor.close()
    return row


async def execute(
    sql: LiteralString,
    params: Iterable[Any] | None = None,
    *,
    autocommit: bool = True
) -> None:
    db = await get_db()
    args: tuple[LiteralString, Iterable[Any] | None] = (sql, params)
    await db.execute(*args)
    if autocommit:
        await db.commit()


def close_db() -> None:
    asyncio.run(_async_close_db())


async def _async_close_db() -> None:
    await (await get_db()).close()


async def _get_cursor(
    sql: LiteralString, params: Iterable[Any] | None
) -> aiosqlite.Cursor:
    db = await get_db()
    args: tuple[LiteralString, Iterable[Any] | None] = (sql, params)
    cursor = await db.execute(*args)
    db.row_factory = aiosqlite.Row
    return cursor


def _get_result_with_column_names(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> dict:
    column_names = [d[0] for d in cursor.description]
    resulting_row = {}
    for index, column_name in enumerate(column_names):
        resulting_row[column_name] = row[index]
    return resulting_row
