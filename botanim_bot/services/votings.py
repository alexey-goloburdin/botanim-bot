from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Iterable

from botanim_bot.services.books import Book
from botanim_bot.services.users import insert_user
from botanim_bot import config
from botanim_bot.db import execute, fetch_one
from botanim_bot.services.exceptions import UserInNotVoteMode, NoActualVoting
from botanim_bot.services.vote_mode import (
    is_user_in_vote_mode,
    remove_user_from_vote_mode,
)


logger = logging.getLogger(__name__)


@dataclass
class Voting:
    id: int
    voting_start: str
    voting_finish: str

    def __post_init__(self):
        """Set up voting_start and voting_finish to needed string format"""
        for field in ("voting_start", "voting_finish"):
            value = getattr(self, field)
            if value is None:
                continue
            try:
                value = datetime.strptime(value, "%Y-%m-%d").strftime(
                    config.DATE_FORMAT
                )
            except ValueError:
                continue
            setattr(self, field, value)


async def get_actual_voting() -> Voting | None:
    sql = """
        SELECT id, voting_start, voting_finish
        FROM voting
        WHERE voting_start <= current_date
            AND voting_finish >= current_date
        ORDER BY voting_start
        LIMIT 1
    """
    voting = await fetch_one(sql)
    if not voting:
        return None
    return Voting(
        id=voting["id"],
        voting_start=voting["voting_start"],
        voting_finish=voting["voting_finish"],
    )


async def save_vote(telegram_user_id: int, books: Iterable[Book]) -> None:
    await insert_user(telegram_user_id)
    if not await is_user_in_vote_mode(telegram_user_id):
        raise UserInNotVoteMode

    actual_voting = await get_actual_voting()
    if actual_voting is None:
        raise NoActualVoting
    sql = """
        INSERT OR REPLACE INTO vote
            (vote_id, user_id, first_book_id, second_book_id, third_book_id)
        VALUES (:vote_id, :user_id, :first_book, :second_book, :third_book)
        """
    books = tuple(books)
    await execute("begin")
    await execute(
        sql,
        {
            "vote_id": actual_voting.id,
            "user_id": telegram_user_id,
            "first_book": books[0].id,
            "second_book": books[1].id,
            "third_book": books[2].id,
        },
        autocommit=False,
    )
    await remove_user_from_vote_mode(telegram_user_id)
    await execute("commit")
