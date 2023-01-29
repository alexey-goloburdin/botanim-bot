from typing import Iterable
from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import Book, format_book_name, get_already_read_books


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    already_read_books = await get_already_read_books()
    response = _build_response(already_read_books)
    await send_response(update, context, response)


def _build_response(already_read_books: Iterable[Book]) -> str:
    books = []
    for index, book in enumerate(already_read_books, 1):
        books.append(_format_book(book, index))
    return message_texts.ALREADY.format(books="\n".join(books))


def _format_book(book: Book, index: int) -> str:
    return message_texts.ALREADY_BOOK.format(
        index=index, book_name=format_book_name(book.name), book=book
    )
