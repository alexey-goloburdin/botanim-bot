from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Iterable

import aiosqlite

from .books import Book
from .users import insert_user
from . import config


@dataclass
class BookVoteResult:
    book_name: str
    score: int


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


@dataclass
class VoteResults:
    voting: Voting
    leaders: list[BookVoteResult]


logger = logging.getLogger(__name__)


async def get_actual_voting() -> Voting | None:
    sql = """
        SELECT id, voting_start, voting_finish
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
            if row is None:
                return None
            return Voting(
                id=row["id"],
                voting_start=row["voting_start"],
                voting_finish=row["voting_finish"],
            )


async def save_vote(telegram_user_id: int, books: Iterable[Book]) -> None:
    await insert_user(telegram_user_id)
    actual_voting = await get_actual_voting()
    if actual_voting is None:
        logger.warning("No actual voting in save_vote()")
        return
    sql = """
        INSERT OR REPLACE INTO vote
            (vote_id, user_id, first_book_id, second_book_id, third_book_id)
        VALUES (:vote_id, :user_id, :first_book, :second_book, :third_book)
        """
    books = tuple(books)
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(
            sql,
            {
                "vote_id": actual_voting.id,
                "user_id": telegram_user_id,
                "first_book": books[0].id,
                "second_book": books[1].id,
                "third_book": books[2].id,
            },
        )
        await db.commit()


async def get_leaders() -> VoteResults | None:
    actual_voting = await get_actual_voting()
    if actual_voting is None:
        return None
    vote_results = VoteResults(
        voting=Voting(
            voting_start=actual_voting.voting_start,
            voting_finish=actual_voting.voting_finish,
            id=actual_voting.id,
        ),
        leaders=[],
    )
    sql = """
        SELECT t2.*, b.name as book_name
        FROM (SELECT t.book_id, sum(t.score) as score from (
            SELECT first_book_id AS book_id, 3*count(*) AS score
            FROM vote v
            WHERE vote_id=(:voting_id)
            GROUP BY first_book_id

            UNION

            SELECT second_book_id AS book_id, 2*count(*) AS score
            FROM vote v
            WHERE vote_id=(:voting_id)
            GROUP BY second_book_id

            UNION

            SELECT third_book_id AS book_id, 1*count(*) AS score
            FROM vote v
            WHERE vote_id=(:voting_id)
            GROUP BY third_book_id
        ) t
        GROUP BY book_id
        ORDER BY sum(t.score) DESC
        LIMIT 10) t2
        LEFT JOIN book b on b.id=t2.book_id
    """
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql, {"voting_id": actual_voting.id}) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                vote_results.leaders.append(
                    BookVoteResult(book_name=row["book_name"], score=row["score"])
                )
    return vote_results
