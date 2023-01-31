from typing import Iterable
from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import (
    Book,
    format_book_name,
    get_next_book,
    get_now_reading_books,
)


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_read_books = await get_now_reading_books()
    next_book = await get_next_book()
    response = _build_response(now_read_books, next_book)
    await send_response(update, context, response)


def _build_response(now_read_books: Iterable[Book], next_book: Book | None) -> str:
    books = []
    for index, book in enumerate(now_read_books, 1):
        prefix = _build_book_prefix(now_read_books, index)
        books.append(_build_book_str(prefix, book, next_book))
    return message_texts.NOW.format(books="\n".join(books))


def _build_book_str(prefix: str, book: Book, next_book: Book | None) -> str:
    return message_texts.NOW_BOOK.format(
        index=f"{prefix}",
        book_name=format_book_name(book.name),
        book=book,
        next_book=_build_next_book(next_book),
    ).strip()


def _build_book_prefix(now_read_books: Iterable[Book], index: int):
    just_one_book = len(tuple(now_read_books)) == 1
    if not just_one_book:
        return f"{index}. "
    else:
        return ""


def _build_next_book(next_book: Book | None) -> str:
    next_book_str = ""
    if next_book:
        next_book_str = message_texts.NEXT_BOOK.format(
            book_name=format_book_name(next_book.name), book=next_book
        )
    return next_book_str
