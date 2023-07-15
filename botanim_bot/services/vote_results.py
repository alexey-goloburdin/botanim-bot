from dataclasses import dataclass
from typing import Iterable, TypedDict, TypeVar, cast

from botanim_bot import config
from botanim_bot.db import fetch_all
from botanim_bot.services import schulze
from botanim_bot.services.books import (
    get_books_info_by_ids,
)
from botanim_bot.services.votings import Voting, get_actual_or_last_voting


@dataclass
class BookVoteResult:
    book_name: str
    positional_number: int


@dataclass
class BooksList:
    books: list[BookVoteResult]


@dataclass
class VoteLeaders:
    voting: Voting
    leaders: list[BooksList]
    votes_count: int


async def get_leaders() -> VoteLeaders | None:
    actual_voting = await get_actual_or_last_voting()
    if actual_voting is None:
        return None

    vote_results_raw = await _get_vote_results(actual_voting.id)

    leaders_ids, candidates_ids = _get_top_leaders_with_schulze(vote_results_raw)

    vote_leaders = await _build_vote_leaders(actual_voting, candidates_ids, leaders_ids)
    vote_leaders.votes_count = _calculate_overall_votes(vote_results_raw)
    return vote_leaders


class VoteRow(TypedDict):
    first_book_id: int
    second_book_id: int
    third_book_id: int
    votes_count: int


def _get_top_leaders_with_schulze(
    vote_results_raw: list[VoteRow],
) -> tuple[list[list[int]], set[int]]:
    candidates, weighted_ranks = _build_data_for_schulze(vote_results_raw)
    leaders = schulze.compute_ranks(candidates, weighted_ranks)
    return leaders[: config.VOTE_RESULTS_TOP], candidates


async def _build_vote_leaders(
    voting: Voting, books_candidates: Iterable[int], leaders: list[list[int]]
) -> VoteLeaders:
    book_id_to_book = await get_books_info_by_ids(books_candidates)
    vote_leaders = _init_vote_results(voting)

    for books_set in leaders:
        book_names = [
            BookVoteResult(
                book_name=book_id_to_book[book].name,
                positional_number=cast(int, book_id_to_book[book].positional_number),
            )
            for book in books_set
        ]
        vote_leaders.leaders.append(BooksList(books=book_names))
    return vote_leaders


def _init_vote_results(voting: Voting) -> VoteLeaders:
    return VoteLeaders(
        voting=Voting(
            voting_start=voting.voting_start,
            voting_finish=voting.voting_finish,
            id=voting.id,
        ),
        leaders=[],
        votes_count=0,
    )


def _calculate_overall_votes(vote_results_rows: list[VoteRow]) -> int:
    return sum((vote["votes_count"] for vote in vote_results_rows))


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
