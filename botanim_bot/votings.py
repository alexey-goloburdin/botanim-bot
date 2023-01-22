import logging
from typing import Iterable

import aiosqlite
from books import Book
from users import insert_user

import config


logger = logging.getLogger(__name__)


async def get_actual_voting_id() -> int | None:
    sql = """
        SELECT id
        FROM voting
        WHERE voting_start <= current_date
            AND voting_finish >= current_date
        ORDER BY voting_start
        LIMIT 1
    """
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            row = await cursor.fetchone()
            if row is None: return None
            return row["id"]


async def save_vote(telegram_user_id: int, books: Iterable[Book]) -> None:
    await insert_user(telegram_user_id)
    actual_voting_id = await get_actual_voting_id()
    if actual_voting_id is None:
        logger.warning("No actual voting in save_vote()")
        return
    sql = """
        INSERT OR REPLACE INTO vote
            (vote_id, user_id, first_book_id, second_book_id, third_book_id)
        VALUES (:vote_id, :user_id, :first_book, :second_book, :third_book)
        """
    books = tuple(books)
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(sql, {
            "vote_id": actual_voting_id,
            "user_id": telegram_user_id,
            "first_book": books[0].id,
            "second_book": books[1].id,
            "third_book": books[2].id,
        })
        await db.commit()
