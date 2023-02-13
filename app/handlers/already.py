from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot.services.books import get_already_read_books
from botanim_bot.templates import render_template


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    already_read_books = await get_already_read_books()
    await send_response(
        update,
        context,
        response=render_template(
            "already.j2", {"already_read_books": already_read_books}
        ),
    )
