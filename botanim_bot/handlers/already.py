from telegram import Update
from telegram.ext import ContextTypes

from .response import send_response
from .. import message_texts
from ..services.books import get_already_read_books


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    already_read_books = await get_already_read_books()
    books = []
    for index, book in enumerate(already_read_books, 1):
        books.append(message_texts.ALREADY_BOOK.format(index=index, book=book))
    response = message_texts.ALREADY.format(books="\n".join(books))
    await send_response(update, context, response)
