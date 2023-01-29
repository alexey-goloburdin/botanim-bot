import re
from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot import config, message_texts
from botanim_bot.handlers.vote import validate_user
from botanim_bot.handlers.response import send_response
from botanim_bot.services.books import Book, get_books_by_positional_numbers
from botanim_bot.services.exceptions import NoActualVoting, UserInNotVoteMode
from botanim_bot.services.num_to_words import books_to_words
from botanim_bot.services.vote_mode import is_user_in_vote_mode
from botanim_bot.services.votings import save_vote


@validate_user
async def vote_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_in_vote_mode(cast(User, update.effective_user).id):
        await send_response(update, context, message_texts.USER_IN_NOT_VOTE_MODE)
        return

    user_message = update.message.text

    books_positional_numbers = _get_numbers_from_text(user_message)
    if not _is_numbers_sufficient(books_positional_numbers):
        await send_response(update, context, message_texts.VOTE_PROCESS_INCORRECT_INPUT)
        return

    finded_books = await get_books_by_positional_numbers(books_positional_numbers)
    if not _is_finded_books_count_sufficient(finded_books):
        await send_response(update, context, message_texts.VOTE_PROCESS_INCORRECT_BOOKS)
        return

    try:
        await save_vote(cast(User, update.effective_user).id, finded_books)
    except NoActualVoting:
        await send_response(update, context, message_texts.NO_ACTUAL_VOTING)
        return
    except UserInNotVoteMode:
        await send_response(update, context, message_texts.USER_IN_NOT_VOTE_MODE)
        return

    await send_response(update, context, _build_response(finded_books))


def _get_numbers_from_text(message: str) -> list[int]:
    return list(map(int, re.findall(r"\d+", message)))


def _is_numbers_sufficient(numbers: list[int]) -> bool:
    return len(numbers) == config.VOTE_ELEMENTS_COUNT


def _is_finded_books_count_sufficient(finded_books: tuple[Book]) -> bool:
    return len(finded_books) == config.VOTE_ELEMENTS_COUNT


def _build_response(finded_books: tuple[Book]) -> str:
    books_formatted = []
    for index, book in enumerate(finded_books, 1):
        books_formatted.append(_get_formatted_book(book=book, index=index))
    books_count = len(books_formatted)
    return message_texts.SUCCESS_VOTE.format(
        books="\n".join(books_formatted),
        books_count=f"{books_count} {books_to_words(books_count)}",
    )


def _get_formatted_book(book: Book, index: int) -> str:
    return message_texts.SUCCESS_VOTE_BOOK.format(index=index, book=book)
