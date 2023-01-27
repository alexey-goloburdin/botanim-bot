import re
from typing import cast

import telegram
from telegram import Update, User
from telegram.ext import ContextTypes

from .response import send_response
from .keyboards import get_categories_keyboard
from .. import message_texts
from ..services.books import (
    build_category_with_books_string,
    calculate_category_books_start_index,
    get_books_by_numbers,
    get_not_started_books,
)
from .. import config
from ..services.votings import get_actual_voting, save_vote
from ..services.num_to_words import books_to_words


async def vote_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await get_actual_voting() is None:
        await send_response(update, context, message_texts.NO_ACTUAL_VOTING)
        return

    user_message = update.message.text
    numbers = re.findall(r"\d+", user_message)
    if len(tuple(set(map(int, numbers)))) != config.VOTE_ELEMENTS_COUNT:
        await send_response(update, context, message_texts.VOTE_PROCESS_INCORRECT_INPUT)
        return
    books = tuple(await get_books_by_numbers(numbers))
    if len(books) != config.VOTE_ELEMENTS_COUNT:
        await send_response(update, context, message_texts.VOTE_PROCESS_INCORRECT_BOOKS)
        return

    await save_vote(cast(User, update.effective_user).id, books)

    books_formatted = []
    for index, book in enumerate(books, 1):
        books_formatted.append(
            message_texts.SUCCESS_VOTE_BOOK.format(index=index, book=book)
        )
    books_count = len(books_formatted)
    await send_response(
        update,
        context,
        message_texts.SUCCESS_VOTE.format(
            books="\n".join(books_formatted),
            books_count=f"{books_count} {books_to_words(books_count)}",
        ),
    )


async def vote_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    categories_with_books = list(await get_not_started_books())

    pattern_prefix_length = len(config.VOTE_BOOKS_CALLBACK_PATTERN)
    current_category_index = int(query.data[pattern_prefix_length:])
    current_category = categories_with_books[current_category_index]

    category_books_start_index = calculate_category_books_start_index(
        categories_with_books, current_category
    )
    await query.edit_message_text(
        text=build_category_with_books_string(
            current_category, category_books_start_index
        ),
        reply_markup=get_categories_keyboard(
            current_category_index,
            len(categories_with_books),
            config.VOTE_BOOKS_CALLBACK_PATTERN,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await get_actual_voting() is None:
        await send_response(update, context, message_texts.NO_ACTUAL_VOTING)
        return

    if not update.message:
        return

    categories_with_books = tuple(await get_not_started_books())
    current_category = categories_with_books[0]

    category_books_start_index = calculate_category_books_start_index(
        categories_with_books, current_category
    )

    await update.message.reply_text(
        build_category_with_books_string(current_category, category_books_start_index),
        reply_markup=get_categories_keyboard(
            0, len(categories_with_books), config.VOTE_BOOKS_CALLBACK_PATTERN
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
