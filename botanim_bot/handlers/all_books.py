import telegram
from telegram import Update
from telegram.ext import ContextTypes


from .response import send_response
from .keyboards import get_categories_keyboard
from ..services.books import build_category_with_books_string, get_all_books
from .. import config


async def all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories_with_books = list(await get_all_books())
    if not update.message:
        return

    await send_response(
        update,
        context,
        build_category_with_books_string(categories_with_books[0]),
        get_categories_keyboard(
            0, len(categories_with_books), config.ALL_BOOKS_CALLBACK_PATTERN
        ),
    )


async def all_books_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    categories_with_books = list(await get_all_books())

    pattern_prefix_length = len(config.ALL_BOOKS_CALLBACK_PATTERN)
    current_category_index = int(query.data[pattern_prefix_length:])
    await query.edit_message_text(
        text=build_category_with_books_string(
            categories_with_books[current_category_index]
        ),
        reply_markup=get_categories_keyboard(
            current_category_index,
            len(categories_with_books),
            config.ALL_BOOKS_CALLBACK_PATTERN,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
