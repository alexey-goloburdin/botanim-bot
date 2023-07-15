import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from botanim_bot import config
from botanim_bot.db import execute, fetch_one
from botanim_bot.services.books import (
    Book,
    format_book_name,
)
from botanim_bot.services.exceptions import NoActualVotingError, UserInNotVoteModeError
from botanim_bot.services.users import insert_user
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

    def is_voting_has_passed(self) -> bool:
        now_date = datetime.now().date()
        finish_voting_date = datetime.strptime(
            self.voting_finish, config.DATE_FORMAT
        ).date()

        return finish_voting_date < now_date

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


@dataclass
class Vote:
    first_book_name: str
    first_book_positional_number: str

    second_book_name: str
    second_book_positional_number: str

    third_book_name: str
    third_book_positional_number: str


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

    return _build_voting(voting)


async def get_actual_or_last_voting() -> Voting | None:
    return await get_actual_voting() or await _get_last_voting()


async def save_vote(telegram_user_id: int, books: Iterable[Book]) -> None:
    await insert_user(telegram_user_id)
    if not await is_user_in_vote_mode(telegram_user_id):
        raise UserInNotVoteModeError

    actual_voting = await get_actual_voting()
    if actual_voting is None:
        raise NoActualVotingError
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


async def get_user_vote(user_id: int, voting_id: int) -> Vote | None:
    sql = """
        WITH pos_numbers AS (
            SELECT
                ROW_NUMBER() OVER (ORDER BY c.ordering, b.ordering) AS rn,
                b.id AS book_id
            FROM book b LEFT JOIN book_category c ON c.id=b.category_id
            WHERE b.read_start IS NULL
        )
        SELECT
            b1.name AS first_book_name,
            b1_pos_number.rn AS first_book_positional_number,
            b2.name AS second_book_name,
            b2_pos_number.rn AS second_book_positional_number,
            b3.name AS third_book_name,
            b3_pos_number.rn AS third_book_positional_number
        FROM vote v
        LEFT JOIN book b1 ON v.first_book_id = b1.id
        LEFT JOIN book b2 ON v.second_book_id = b2.id
        LEFT JOIN book b3 ON v.third_book_id = b3.id
        LEFT JOIN pos_numbers AS b1_pos_number ON b1_pos_number.book_id=b1.id
        LEFT JOIN pos_numbers AS b2_pos_number ON b2_pos_number.book_id=b2.id
        LEFT JOIN pos_numbers AS b3_pos_number ON b3_pos_number.book_id=b3.id
        WHERE v.user_id=:user_id
            AND v.vote_id=:voting_id
    """
    vote = await fetch_one(sql, {"user_id": user_id, "voting_id": voting_id})
    if not vote:
        return None
    user_vote = {
        field: format_book_name(vote[field])
        for field in (
            "first_book_name",
            "second_book_name",
            "third_book_name",
        )
    }
    user_vote.update(
        {
            k: vote[k]
            for k in (
                "first_book_positional_number",
                "second_book_positional_number",
                "third_book_positional_number",
            )
        }
    )
    return Vote(**user_vote)


def _build_voting(voting_db_row: dict) -> Voting:
    return Voting(
        id=voting_db_row["id"],
        voting_start=voting_db_row["voting_start"],
        voting_finish=voting_db_row["voting_finish"],
    )


async def _get_last_voting() -> Voting | None:
    sql = """
        SELECT id, voting_start, voting_finish
        FROM voting
        WHERE voting_finish < current_date
        ORDER BY voting_finish desc
        LIMIT 1
    """
    last_voting = await fetch_one(sql)
    if not last_voting:
        return None

    return _build_voting(last_voting)
