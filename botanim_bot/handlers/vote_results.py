from datetime import datetime
from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot import config
from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import format_book_name
from botanim_bot.services.vote_results import (
    BookVoteResult,
    BooksList,
    VoteLeaders,
    get_leaders,
)
from botanim_bot.services.votings import Vote, Voting, get_user_vote


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = await get_leaders()
    if leaders is None:
        await send_response(
            update, context, message_texts.VOTE_RESULTS_NO_ACTUAL_VOTING
        )
        return

    your_vote = await get_user_vote(
        cast(User, update.effective_user).id, leaders.voting.id
    )
    response = _build_response(leaders, your_vote)
    await send_response(update, context, response)


def is_voting_has_passed(voting: Voting):
    return (
        datetime.now().date()
        > datetime.strptime(voting.voting_finish, config.DATE_FORMAT).date()
    )


def _build_response(leaders: VoteLeaders, your_vote: Vote | None) -> str:
    is_voting_has_passed_ = is_voting_has_passed(leaders.voting)
    return message_texts.VOTE_RESULTS.format(
        voting_type=("прошедшего" if is_voting_has_passed_ else "текущего"),
        books=_get_books_list_formatted(leaders),
        voting_start=leaders.voting.voting_start,
        voting_finish=leaders.voting.voting_finish,
        votes_count=leaders.votes_count,
        your_vote=_get_your_vote_formatted(your_vote, is_voting_has_passed_),
    )


def _get_books_list_formatted(leaders: VoteLeaders) -> str:
    books = []
    for rank_number, books_in_the_rank in enumerate(leaders.leaders, 1):
        books.append(_get_books_in_the_rank_formatted(books_in_the_rank, rank_number))
    return "\n".join(books) if books else message_texts.VOTE_RESULTS_ZERO_VOTES


def _get_books_in_the_rank_formatted(
    books_in_the_rank: BooksList, rank_number: int
) -> str:
    if len(books_in_the_rank.books) == 1:
        book_str = _get_book_formatted(books_in_the_rank.books[0])
    else:
        books_str = "\n    ".join(
            [_get_book_formatted(book) for book in books_in_the_rank.books]
        )
        book_str = message_texts.VOTE_RESULT_SEVERAL_BOOKS.format(books=books_str)
    return message_texts.VOTE_RESULT_BOOK.format(index=rank_number, book=book_str)


def _get_book_formatted(book: BookVoteResult) -> str:
    return format_book_name(book.book_name)


def _get_your_vote_formatted(
    your_vote: Vote | None, is_voting_has_passed_: bool
) -> str:
    if not your_vote:
        return message_texts.VOTE_RESULTS_YOUR_VOTE_NOT_EXISTS
    book_names = map(
        format_book_name,
        (
            your_vote.first_book_name,
            your_vote.second_book_name,
            your_vote.third_book_name,
        ),
    )
    book_names = "\n".join(
        [f"{index}. {book_name}" for index, book_name in enumerate(book_names, 1)]
    )
    return message_texts.VOTE_RESULTS_YOUR_VOTE_EXISTS.format(
        books=book_names,
        revote=message_texts.REVOTE if not is_voting_has_passed_ else "",
    )
