import re
from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot import config
from botanim_bot.handlers.vote import validate_user
from botanim_bot.handlers.response import send_response
from botanim_bot.services.books import Book, get_books_by_positional_numbers
from botanim_bot.services.exceptions import NoActualVoting, UserInNotVoteMode
from botanim_bot.services.num_to_words import books_to_words
from botanim_bot.services.vote_mode import is_user_in_vote_mode
from botanim_bot.services.votings import save_vote
from botanim_bot.templates import render_template


@validate_user
async def vote_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_in_vote_mode(cast(User, update.effective_user).id):
        await send_response(
            update, context, response=render_template("vote_user_not_in_right_mode.j2")
        )
        return

    user_message = update.message.text

    books_positional_numbers = _get_numbers_from_text(user_message)
    if not _is_numbers_sufficient(books_positional_numbers):
        await send_response(
            update, context, response=render_template("vote_incorrect_input.j2")
        )
        return

    selected_books = await get_books_by_positional_numbers(books_positional_numbers)
    if not _is_finded_books_count_sufficient(selected_books):
        await send_response(
            update, context, render_template("vote_incorrect_books.j2")
        )
        return

    try:
        await save_vote(cast(User, update.effective_user).id, selected_books)
    except NoActualVoting:
        await send_response(
            update, context, response=render_template("vote_no_actual_voting.j2")
        )
        return
    except UserInNotVoteMode:
        await send_response(
            update, context, response=render_template("vote_user_not_in_right_mode.j2")
        )
        return

    books_count = len(selected_books)
    await send_response(
        update,
        context,
        response=render_template(
            "vote_success.j2",
            {
                "selected_books": selected_books,
                "books_count": f"{books_count} {books_to_words(books_count)}",
            },
        ),
    )


def _get_numbers_from_text(message: str) -> list[int]:
    return list(map(int, re.findall(r"\d+", message)))


def _is_numbers_sufficient(numbers: list[int]) -> bool:
    return len(numbers) == config.VOTE_ELEMENTS_COUNT


def _is_finded_books_count_sufficient(finded_books: tuple[Book]) -> bool:
    return len(finded_books) == config.VOTE_ELEMENTS_COUNT
