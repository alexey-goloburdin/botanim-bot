from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import format_book_name
from botanim_bot.services.vote_results import VoteResults, get_leaders
from botanim_bot.services.votings import Vote, get_user_actual_vote


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = await get_leaders()
    if leaders is None:
        await send_response(
            update, context, message_texts.VOTE_RESULTS_NO_ACTUAL_VOTING
        )
        return

    your_vote = await get_user_actual_vote(cast(User, update.effective_user).id)
    response = _build_response(leaders, your_vote)
    await send_response(update, context, response)


def _get_books_list_formatted(leaders: VoteResults) -> str:
    books = []
    for rank_number, books_in_the_rank in enumerate(leaders.leaders, 1):
        if len(books_in_the_rank) == 1:
            book_str = format_book_name(books_in_the_rank[0].book_name)
        else:
            books_str = "\n    ".join(
                [format_book_name(book.book_name) for book in books_in_the_rank]
            )
            book_str = message_texts.VOTE_RESULT_SEVERAL_BOOKS.format(books=books_str)
        books.append(
            message_texts.VOTE_RESULT_BOOK.format(index=rank_number, book=book_str)
        )
    return "\n".join(books) if books else message_texts.VOTE_RESULTS_ZERO_VOTES


def _get_your_vote_formatted(your_vote: Vote | None) -> str:
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
    return message_texts.VOTE_RESULTS_YOUR_VOTE_EXISTS.format(books=book_names)


def _build_response(leaders: VoteResults, your_vote: Vote | None) -> str:
    return message_texts.VOTE_RESULTS.format(
        books=_get_books_list_formatted(leaders),
        voting_start=leaders.voting.voting_start,
        voting_finish=leaders.voting.voting_finish,
        votes_count=leaders.votes_count,
        your_vote=_get_your_vote_formatted(your_vote),
    )
