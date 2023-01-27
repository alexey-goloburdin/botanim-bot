from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import get_already_read_books


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    already_read_books = await get_already_read_books()
    books = []
    for index, book in enumerate(already_read_books, 1):
        books.append(message_texts.ALREADY_BOOK.format(index=index, book=book))
    response = message_texts.ALREADY.format(books="\n".join(books))
    await send_response(update, context, response)
