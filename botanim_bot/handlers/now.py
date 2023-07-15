from typing import cast

from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot import config
from botanim_bot.handlers.response import send_response
from botanim_bot.services.books import get_next_book, get_now_reading_books
from botanim_bot.services.validation import is_user_in_channel
from botanim_bot.templates import render_template


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_read_books = await get_now_reading_books()
    next_book = await get_next_book()

    user_id = cast(User, update.effective_user).id
    if not await is_user_in_channel(user_id, config.TELEGRAM_BOTANIM_CHANNEL_ID):
        template = "now.j2"
    else:
        template = "now_for_member.j2"
    await send_response(
        update,
        context,
        response=render_template(
            template, {"now_read_books": now_read_books, "next_book": next_book}
        ),
    )
