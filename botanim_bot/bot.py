import logging
import os
import re
from typing import Iterable

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
import message_texts
from books import (
    get_all_books,
    get_already_read_books,
    get_now_reading_books,
    get_not_started_books,
    get_books_by_numbers,
    build_category_with_books_string,
    calculate_category_books_start_index,
    format_book_name,
    Category,
)
from num_to_words import books_to_words
from votings import save_vote, get_actual_voting, get_leaders

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_USERNAME = os.getenv("TELEGRAM_ADMIN_USERNAME")
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_USERNAME:
    exit("Specify TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_USERNAME env variables")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /start")
        return
    await context.bot.send_message(
        chat_id=effective_chat.id, text=message_texts.GREETINGS
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /help")
        return
    await context.bot.send_message(chat_id=effective_chat.id, text=message_texts.HELP)


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /already")
        return
    already_read_books = await get_already_read_books()
    response = "Прочитанные книги:\n\n"
    for index, book in enumerate(already_read_books, 1):
        response += (
            f"{index}. {book.name} "
            f"(читали с {book.read_start} по {book.read_finish})\n"
        )
    await context.bot.send_message(chat_id=effective_chat.id, text=response)


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /now")
        return
    now_read_books = tuple(await get_now_reading_books())
    response = "Сейчас мы читаем:\n\n"
    just_one_book = len(now_read_books) == 1
    for index, book in enumerate(now_read_books, 1):
        response += (
            f"{str(index) + '. ' if not just_one_book else ''}"
            f"{book.name} "
            f"(с {book.read_start} по {book.read_finish})\n"
        )
    await context.bot.send_message(chat_id=effective_chat.id, text=response)


async def vote_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /vote_process")
        return

    if await get_actual_voting() is None:
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.NO_ACTUAL_VOTING,
            parse_mode=telegram.constants.ParseMode.HTML,
        )
        return

    user_message = update.message.text
    numbers = re.findall(r"\d+", user_message)
    if len(tuple(set(map(int, numbers)))) != config.VOTE_ELEMENTS_COUNT:
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.VOTE_PROCESS_INCORRECT_INPUT,
            parse_mode=telegram.constants.ParseMode.HTML,
        )
        return
    books = tuple(await get_books_by_numbers(numbers))
    if len(books) != config.VOTE_ELEMENTS_COUNT:
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.VOTE_PROCESS_INCORRECT_BOOKS,
            parse_mode=telegram.constants.ParseMode.HTML,
        )
        return

    # TODO move to message_texts module all hardcoded texts
    await save_vote(update.effective_user.id, books)

    books_formatted = []
    for index, book in enumerate(books, 1):
        books_formatted.append(f"{index}. {book.name}")
    books_count = len(books_formatted)
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=message_texts.SUCCESS_VOTE.format(
            books="\n".join(books_formatted),
            books_count=f"{books_count} {books_to_words(books_count)}",
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /vote_results")
        return
    leaders = await get_leaders()
    if leaders is None:
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.NO_VOTE_RESULTS,
            parse_mode=telegram.constants.ParseMode.HTML,
        )
        return

    books = []
    for index, book in enumerate(leaders.leaders, 1):
        books.append(
            f"{index}. {format_book_name(book.book_name)}. " f"Рейтинг: {book.score}"
        )
    response = message_texts.VOTE_RESULTS.format(
        books="\n".join(books),
        voting_start=leaders.voting.voting_start,
        voting_finish=leaders.voting.voting_finish,
    )
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=response,
        parse_mode=telegram.constants.ParseMode.HTML,
    )


def _get_category_switcher_keyboard(
    current_index: int, overall_count: int, prefix: str
) -> InlineKeyboardMarkup:
    prev_category_index = current_index - 1
    if prev_category_index < 0:
        prev_category_index = overall_count - 1
    next_category_index = current_index + 1
    if next_category_index > overall_count - 1:
        next_category_index = 0

    # TODO: change keyboard callback data generation out of Telegram's limitations (1-64 characters) to avoid errors
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"{prefix}{prev_category_index}"),
            InlineKeyboardButton(
                str(current_index + 1) + "/" + str(overall_count),
                callback_data=f"{prefix}{config.CATEGORIES_LIST_CALLBACK_PATTERN}{current_index}"
            ),
            InlineKeyboardButton(
                ">",
                callback_data=f"{prefix}{next_category_index}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def _get_boards_count(overall_count: int, categories_count_per_board: int) -> int:
    return overall_count // categories_count_per_board


def _get_board_index_by_category_index(category_index: int, categories_count_per_board: int) -> int:
    return category_index // categories_count_per_board


def _get_categories_list_keyboard(
    categories: Iterable[Category], board_index: int, category_index: int, overall_categories_count: int,
    prefix: str, categories_count_per_board: int = config.CATEGORIES_PER_BOARD
) -> InlineKeyboardMarkup:
    boards_count = _get_boards_count(overall_categories_count, categories_count_per_board)

    previous_index = board_index - 1
    if previous_index < 0:
        previous_index = boards_count - 1
    next_index = board_index + 1
    if next_index > boards_count - 1:
        next_index = 0

    keyboard = []

    first_board_category_index = board_index * categories_count_per_board
    for category in categories[first_board_category_index:first_board_category_index + categories_count_per_board]:
        keyboard.append([InlineKeyboardButton(
            category.name,
            callback_data=f"{prefix}{config.SELECT_CATEGORY_PATTERN}{category.id - 1}"
        )])

    keyboard.append([
        InlineKeyboardButton(
            "<",
            callback_data=f"{prefix}{config.CATEGORIES_LIST_CALLBACK_PATTERN}{previous_index}/{category_index}"
        ),
        InlineKeyboardButton(
            str(board_index + 1) + "/" + str(boards_count),
            callback_data=f"{prefix}{config.CATEGORIES_LIST_CALLBACK_PATTERN}hide/{category_index}"
        ),
        InlineKeyboardButton(
            ">",
            callback_data=f"{prefix}{config.CATEGORIES_LIST_CALLBACK_PATTERN}{next_index}/{category_index}",
        ),
    ])
    return InlineKeyboardMarkup(keyboard)


async def vote_button(update: Update, _):
    query = update.callback_query
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
        reply_markup=_get_category_switcher_keyboard(
            current_category_index,
            len(categories_with_books),
            config.VOTE_BOOKS_CALLBACK_PATTERN,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /vote")
        return

    if await get_actual_voting() is None:
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.NO_ACTUAL_VOTING,
            parse_mode=telegram.constants.ParseMode.HTML,
        )
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
        reply_markup=_get_category_switcher_keyboard(
            0, len(categories_with_books), config.VOTE_BOOKS_CALLBACK_PATTERN
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )

    """
    index = 1
    for category in categories_with_books:
        response = "<b>" + category.name + "</b>\n\n"
        for book in category.books:
            response += f"{index}. {book.name}\n"
            index += 1
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=response,
            parse_mode=telegram.constants.ParseMode.HTML,
        )
        await asyncio.sleep(config.SLEEP_BETWEEN_MESSAGES_TO_ONE_USER)
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=message_texts.VOTE,
        parse_mode=telegram.constants.ParseMode.HTML,
    )
    """
    return


async def all_books(update: Update, _: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /allbooks")
        return

    categories_with_books = list(await get_all_books())
    if not update.message:
        return

    await update.message.reply_text(
        build_category_with_books_string(categories_with_books[0]),
        reply_markup=_get_category_switcher_keyboard(
            0, len(categories_with_books), config.ALL_BOOKS_CALLBACK_PATTERN
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def all_books_button(update: Update, _):
    query = update.callback_query
    if not query.data or not query.data.strip():
        return
    categories_with_books = list(await get_all_books())

    pattern_prefix_length = len(config.ALL_BOOKS_CALLBACK_PATTERN)
    query_without_pattern = query.data[pattern_prefix_length:]

    current_category_index = int(query_without_pattern)

    await query.edit_message_text(
        text=build_category_with_books_string(
            categories_with_books[current_category_index]
        ),
        reply_markup=_get_category_switcher_keyboard(
            current_category_index,
            len(categories_with_books),
            config.ALL_BOOKS_CALLBACK_PATTERN,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def select_all_books_category_button(update: Update, _):
    query = update.callback_query
    if not query.data or not query.data.strip():
        return

    categories_with_books = list(await get_all_books())

    pattern_prefix_length = len(config.ALL_BOOKS_CALLBACK_PATTERN) + len(config.SELECT_CATEGORY_PATTERN)
    query_without_pattern = query.data[pattern_prefix_length:]

    current_category_index = int(query_without_pattern)

    await query.edit_message_text(
        text=build_category_with_books_string(
            categories_with_books[current_category_index]
        ),
        reply_markup=_get_category_switcher_keyboard(
            current_category_index,
            len(categories_with_books),
            config.ALL_BOOKS_CALLBACK_PATTERN,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def show_all_books_categories_button(update: Update, _):
    query = update.callback_query
    if not query.data or not query.data.strip():
        return
    categories_with_books = list(await get_all_books())

    pattern_prefix_length = len(config.ALL_BOOKS_CALLBACK_PATTERN) + len(config.CATEGORIES_LIST_CALLBACK_PATTERN)
    query_without_pattern = query.data[pattern_prefix_length:]

    current_category_index = int(query_without_pattern)

    await query.edit_message_reply_markup(
        reply_markup=_get_categories_list_keyboard(
            categories_with_books,
            _get_board_index_by_category_index(current_category_index, config.CATEGORIES_PER_BOARD),
            current_category_index,
            len(categories_with_books),
            config.ALL_BOOKS_CALLBACK_PATTERN
        )
    )


async def all_books_categories_list_button(update: Update, _):
    query = update.callback_query
    if not query.data or not query.data.strip():
        return

    categories_with_books = list(await get_all_books())

    pattern_prefix_length = len(config.ALL_BOOKS_CALLBACK_PATTERN) + len(config.CATEGORIES_LIST_CALLBACK_PATTERN)
    query_without_prefix = query.data[pattern_prefix_length:]

    action, current_category_index = query_without_prefix.split("/")
    if action == "hide":
        await query.edit_message_reply_markup(
            reply_markup=_get_category_switcher_keyboard(
                int(current_category_index),
                len(categories_with_books),
                config.ALL_BOOKS_CALLBACK_PATTERN,
            ),
        )
        return
    elif action.isdigit():
        await query.edit_message_reply_markup(
            reply_markup=_get_categories_list_keyboard(
                categories_with_books,
                int(action),
                int(current_category_index),
                len(categories_with_books),
                config.ALL_BOOKS_CALLBACK_PATTERN,
            ),
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler(
        "start", start, filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME)
    )
    application.add_handler(start_handler)

    help_handler = CommandHandler(
        "help", help, filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME)
    )
    application.add_handler(help_handler)

    all_books_handler = CommandHandler(
        "allbooks",
        all_books,
        filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME),
    )
    application.add_handler(all_books_handler)
    application.add_handler(
        CallbackQueryHandler(
            all_books_button,
            pattern="^" + config.ALL_BOOKS_CALLBACK_PATTERN + r"(\d+)$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            select_all_books_category_button,
            pattern="^" + config.ALL_BOOKS_CALLBACK_PATTERN + config.SELECT_CATEGORY_PATTERN + r"(\d+)$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            show_all_books_categories_button,
            pattern="^" + config.ALL_BOOKS_CALLBACK_PATTERN + config.CATEGORIES_LIST_CALLBACK_PATTERN + r"(\d+)$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            all_books_categories_list_button,
            pattern="^" + config.ALL_BOOKS_CALLBACK_PATTERN + config.CATEGORIES_LIST_CALLBACK_PATTERN + r"(.+)/",
        )
    )

    already_handler = CommandHandler(
        "already", already, filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME)
    )
    application.add_handler(already_handler)

    now_handler = CommandHandler(
        "now", now, filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME)
    )
    application.add_handler(now_handler)

    vote_handler = CommandHandler(
        "vote", vote, filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME)
    )
    application.add_handler(vote_handler)
    application.add_handler(
        CallbackQueryHandler(
            vote_button,
            pattern="^" + config.VOTE_BOOKS_CALLBACK_PATTERN + r"(\d+)$",
        )
    )

    vote_process_handler = MessageHandler(
        filters.User(username="@" + TELEGRAM_ADMIN_USERNAME)
        & filters.TEXT
        & (~filters.COMMAND),
        vote_process,
    )
    application.add_handler(vote_process_handler)

    vote_results_handler = CommandHandler(
        "voteresults",
        vote_results,
        filters=filters.User(username="@" + TELEGRAM_ADMIN_USERNAME),
    )
    application.add_handler(vote_results_handler)

    application.run_polling()
