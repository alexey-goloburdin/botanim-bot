from telegram import Update
from telegram.ext import ContextTypes

from .response import send_response
from .. import message_texts
from ..services.books import get_now_reading_books


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_read_books = await get_now_reading_books()
    books = []
    just_one_book = len(tuple(now_read_books)) == 1
    for index, book in enumerate(now_read_books, 1):
        books.append(
            message_texts.NOW_BOOK.format(
                index=str(index) + ". " if not just_one_book else "", book=book
            )
        )
    response = message_texts.NOW.format(books="\n".join(books))
    await send_response(update, context, response)
