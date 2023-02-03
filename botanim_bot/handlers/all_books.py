import telegram
from telegram import Update
from telegram.ext import ContextTypes


from botanim_bot.handlers.response import send_response
from botanim_bot.handlers.keyboards import get_categories_keyboard
from botanim_bot.services.books import get_all_books
from botanim_bot import config
from botanim_bot.templates import render_template


async def all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories_with_books = list(await get_all_books())
    if not update.message:
        return

    await send_response(
        update,
        context,
        render_template(
            "category_with_books.j2",
            {"category": categories_with_books[0], "start_index": None},
        ),
        get_categories_keyboard(
            current_category_index=0,
            categories_count=len(categories_with_books),
            callback_prefix=config.ALL_BOOKS_CALLBACK_PATTERN,
        ),
    )


async def all_books_button(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    categories_with_books = list(await get_all_books())
    current_category_index = _get_current_category_index(query.data)
    await query.edit_message_text(
        text=render_template(
            "category_with_books.j2",
            {
                "category": categories_with_books[current_category_index],
                "start_index": None,
            },
        ),
        reply_markup=get_categories_keyboard(
            current_category_index=current_category_index,
            categories_count=len(categories_with_books),
            callback_prefix=config.ALL_BOOKS_CALLBACK_PATTERN,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


def _get_current_category_index(query_data) -> int:
    pattern_prefix_length = len(config.ALL_BOOKS_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])
