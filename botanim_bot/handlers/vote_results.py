from telegram import Update
from telegram.ext import ContextTypes

from .response import send_response
from .. import message_texts
from ..services.books import format_book_name
from ..services.votings import get_leaders


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = await get_leaders()
    if leaders is None:
        await send_response(update, context, message_texts.NO_VOTE_RESULTS)
        return

    books = []
    for index, book in enumerate(leaders.leaders, 1):
        books.append(
            message_texts.VOTE_RESULT_BOOK.format(
                index=index,
                book_name=format_book_name(book.book_name),
                book_score=book.score,
            )
        )
    response = message_texts.VOTE_RESULTS.format(
        books="\n".join(books),
        voting_start=leaders.voting.voting_start,
        voting_finish=leaders.voting.voting_finish,
    )
    await send_response(update, context, response)
