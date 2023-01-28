from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.vote_results import get_leaders
from botanim_bot.services.votings import get_user_actual_vote


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = await get_leaders()
    if leaders is None:
        await send_response(update, context, message_texts.NO_VOTE_RESULTS)
        return

    books = []
    for index, books_set in enumerate(leaders.leaders, 1):
        if len(books_set) == 1:
            book_str = books_set[0].book_name
        else:
            book_str = message_texts.VOTE_RESULT_SEVERAL_BOOKS.format(
                books="    " + "\n    ".join([book.book_name for book in books_set])
            )
        books.append(message_texts.VOTE_RESULT_BOOK.format(index=index, book=book_str))
    your_vote = await get_user_actual_vote(cast(User, update.effective_user).id)
    if your_vote:
        your_vote_str = message_texts.VOTE_RESULTS_YOUR_VOTE_EXISTS.format(
            books=(
                f"1. {your_vote.first_book_name}\n"
                f"2. {your_vote.second_book_name}\n"
                f"3. {your_vote.third_book_name}"
            )
        )
    else:
        your_vote_str = message_texts.VOTE_RESULTS_YOUR_VOTE_NOT_EXISTS
    response = message_texts.VOTE_RESULTS.format(
        books="\n".join(books) if books else message_texts.VOTE_RESULTS_ZERO_VOTES,
        voting_start=leaders.voting.voting_start,
        voting_finish=leaders.voting.voting_finish,
        votes_count=leaders.votes_count,
        your_vote=your_vote_str,
    )
    await send_response(update, context, response)
