from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.books import get_now_reading_books


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_read_books = await get_now_reading_books()
    books = []
    just_one_book = len(tuple(now_read_books)) == 1
    for index, book in enumerate(now_read_books, 1):
        if not just_one_book:
            prefix = f"{index}. "
        else:
            prefix = ""
        books.append(message_texts.NOW_BOOK.format(index=f"{prefix}", book=book))
    response = message_texts.NOW.format(books="\n".join(books))
    await send_response(update, context, response)
