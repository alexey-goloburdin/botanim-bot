from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot.services.books import (
    get_next_book,
    get_now_reading_books,
)
from botanim_bot.templates import render_template


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_read_books = await get_now_reading_books()
    next_book = await get_next_book()
    await send_response(
        update,
        context,
        response=render_template(
            "now.j2", {"now_read_books": now_read_books, "next_book": next_book}
        ),
    )
