from typing import Iterable
from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import Book, format_book_name, get_now_reading_books


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_read_books = await get_now_reading_books()
    response = _build_response(now_read_books)
    await send_response(update, context, response)


def _build_response(now_read_books: Iterable[Book]) -> str:
    books = []
    for index, book in enumerate(now_read_books, 1):
        prefix = _get_book_prefix(now_read_books, index)
        books.append(
            message_texts.NOW_BOOK.format(
                index=f"{prefix}", book_name=format_book_name(book.name), book=book
            )
        )
    return message_texts.NOW.format(books="\n".join(books))


def _get_book_prefix(now_read_books: Iterable[Book], index: int):
    just_one_book = len(tuple(now_read_books)) == 1
    if not just_one_book:
        return f"{index}. "
    else:
        return ""
