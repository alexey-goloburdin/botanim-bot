from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.vote_results import get_leaders


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = await get_leaders()
    if leaders is None:
        await send_response(update, context, message_texts.NO_VOTE_RESULTS)
        return

    books = []
    for index, books_set in enumerate(leaders.leaders, 1):
        if len(books_set) == 1:
            books_str = books_set[0].book_name
        else:
            books_str = message_texts.VOTE_RESULT_SEVERAL_BOOKS.format(
                books="    " + "\n    ".join([book.book_name for book in books_set])
            )
        books.append(
            message_texts.VOTE_RESULT_BOOK.format(index=index, books=books_str)
        )
    response = message_texts.VOTE_RESULTS.format(
        books="\n".join(books) if books else message_texts.VOTE_RESULTS_ZERO_VOTES,
        voting_start=leaders.voting.voting_start,
        voting_finish=leaders.voting.voting_finish,
        votes_count=leaders.votes_count,
    )
    await send_response(update, context, response)
