from dataclasses import dataclass
from typing import Iterable, TypeVar, TypedDict, cast

from botanim_bot import config
from botanim_bot.db import fetch_all
from botanim_bot.services.books import get_book_names_by_ids
from botanim_bot.services.votings import Voting, get_actual_voting
from botanim_bot.services import schulze


@dataclass
class BookVoteResult:
    book_name: str


@dataclass
class BooksSetScores:
    books: list[BookVoteResult]
    score: int


@dataclass
class VoteResults:
    voting: Voting
    leaders: list[BooksSetScores]
    votes_count: int


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
        votes_count=0,
    )
    rows = await _get_vote_results(actual_voting.id)
    vote_results.votes_count = sum((vote["votes_count"] for vote in rows))
    books, weighted_ranks = _build_data_for_schulze(rows)
    best = schulze.compute_ranks(books, weighted_ranks)
    best = best[: config.VOTE_RESULTS_TOP]
    book_id_to_name = await get_book_names_by_ids(books)
    for books_set, score in best:
        book_names = [
            BookVoteResult(book_name=book_id_to_name[book]) for book in books_set
        ]
        vote_results.leaders.append(BooksSetScores(books=book_names, score=score))
    return vote_results


class VoteRow(TypedDict):
    first_book_id: int
    second_book_id: int
    third_book_id: int
    votes_count: int


async def _get_vote_results(vote_id: int) -> list[VoteRow]:
    sql = """
        select
            first_book_id,
            second_book_id,
            third_book_id,
            count(*) as votes_count
        from vote
        where vote_id=:vote_id
        group by 1, 2, 3
    """
    return cast(list[VoteRow], await fetch_all(sql, {"vote_id": vote_id}))


def _build_data_for_schulze(
    rows,
) -> tuple[set[int], list[tuple[list[list[int]], int]]]:
    candidate_books = set()
    weighted_ranks = []

    for row in rows:
        candidate_books.update(
            [row["first_book_id"], row["second_book_id"], row["third_book_id"]]
        )

        weighted_ranks.append((_prepare_weighted_ranks(row), row["votes_count"]))

    return candidate_books, weighted_ranks


def _prepare_weighted_ranks(row: VoteRow) -> list[list[int]]:
    book_ids = [row["first_book_id"], row["second_book_id"], row["third_book_id"]]
    book_ids_withot_duplicates = _remove_duplicates_with_save_order(book_ids)
    return [[book_id] for book_id in book_ids_withot_duplicates]


T = TypeVar("T")


def _remove_duplicates_with_save_order(elements: Iterable[T]) -> Iterable[T]:
    return list(dict.fromkeys(elements))
