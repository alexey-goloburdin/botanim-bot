import asyncio
from datetime import datetime 
import os
import re

import logging
import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters)

from books import (
    get_all_books,
    get_already_read_books,
    get_now_reading_books,
    get_not_started_books,
    get_books_by_numbers
)
from votings import (
    save_vote,
    get_actual_voting_id
)
import config
import message_texts


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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
            chat_id=effective_chat.id,
            text=message_texts.GREETINGS)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /help")
        return
    await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.HELP)


async def all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /allbooks")
        return
    categories_with_books = await get_all_books()
    for category in categories_with_books:
        response = "<b>" + category.name + "</b>\n\n"
        for index, book in enumerate(category.books, 1):
            response += f"{index}. {book.name}\n"
        await context.bot.send_message(
                chat_id=effective_chat.id,
                text=response,
                parse_mode=telegram.constants.ParseMode.HTML)
        await asyncio.sleep(config.SLEEP_BETWEEN_MESSAGES_TO_ONE_USER)


async def already(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /help")
        return
    already_read_books = await get_already_read_books()
    response = "Прочитанные книги:\n\n"
    for index, book in enumerate(already_read_books, 1):
        response += (f"{index}. {book.name} "
                     f"(читали с {book.read_start} по {book.read_finish})\n")
    await context.bot.send_message(
            chat_id=effective_chat.id,
            text=response)


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /help")
        return
    now_read_books = await get_now_reading_books()
    response = "Сейчас мы читаем:\n\n"
    just_one_book = len(now_read_books) == 1
    for index, book in enumerate(now_read_books, 1):
        response += (f"{str(index) + '. ' if not just_one_book else ''}"
                     f"{book.name} "
                     f"(с {book.read_start} по {book.read_finish})\n")
    await context.bot.send_message(
            chat_id=effective_chat.id,
            text=response)


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /allbooks")
        return

    if await get_actual_voting_id() is None:
        await context.bot.send_message(
                chat_id=effective_chat.id,
                text=message_texts.NO_ACTUAL_VOTING,
                parse_mode=telegram.constants.ParseMode.HTML)
        return

    categories_with_books = await get_not_started_books()
    index = 1
    for category in categories_with_books:
        response = "<b>" + category.name + "</b>\n\n"
        for book in category.books:
            response += f"{index}. {book.name}\n"
            index += 1
        await context.bot.send_message(
                chat_id=effective_chat.id,
                text=response,
                parse_mode=telegram.constants.ParseMode.HTML)
        await asyncio.sleep(config.SLEEP_BETWEEN_MESSAGES_TO_ONE_USER)
    await context.bot.send_message(
            chat_id=effective_chat.id,
            text=message_texts.VOTE,
            parse_mode=telegram.constants.ParseMode.HTML)


async def vote_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /allbooks")
        return

    if await get_actual_voting_id() is None:
        await context.bot.send_message(
                chat_id=effective_chat.id,
                text=message_texts.NO_ACTUAL_VOTING,
                parse_mode=telegram.constants.ParseMode.HTML)
        return

    user_message = update.message.text
    numbers = re.findall(r"\d+", user_message)
    if len(tuple(set(map(int, numbers)))) != config.VOTE_ELEMENTS_COUNT:
        await context.bot.send_message(
                chat_id=effective_chat.id,
                text=message_texts.VOTE_PROCESS_INCORRECT_INPUT,
                parse_mode=telegram.constants.ParseMode.HTML)
        return
    books = await get_books_by_numbers(numbers)
    if len(books) != config.VOTE_ELEMENTS_COUNT:
        await context.bot.send_message(
                chat_id=effective_chat.id,
                text=message_texts.VOTE_PROCESS_INCORRECT_BOOKS,
                parse_mode=telegram.constants.ParseMode.HTML)
        return

    # TODO move to message_texts module all hardcoded texts
    # «три книги» correspond to config.VOTE_ELEMENTS_COUNT
    await save_vote(update.effective_user.id, books)

    response = "Ура, ты выбрал три книги:\n\n"
    for index, book in enumerate(books, 1):
        response += f"{index}. {book.name}\n"
    await context.bot.send_message(
            chat_id=effective_chat.id,
            text=response,
            parse_mode=telegram.constants.ParseMode.HTML)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start,
               filters=filters.User(username="@"+TELEGRAM_ADMIN_USERNAME))
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help,
               filters=filters.User(username="@"+TELEGRAM_ADMIN_USERNAME))
    application.add_handler(help_handler)
    
    all_books_handler = CommandHandler('allbooks', all_books,
               filters=filters.User(username="@"+TELEGRAM_ADMIN_USERNAME))
    application.add_handler(all_books_handler)

    already_handler = CommandHandler('already', already,
               filters=filters.User(username="@"+TELEGRAM_ADMIN_USERNAME))
    application.add_handler(already_handler)

    now_handler = CommandHandler('now', now,
               filters=filters.User(username="@"+TELEGRAM_ADMIN_USERNAME))
    application.add_handler(now_handler)

    vote_handler = CommandHandler('vote', vote,
               filters=filters.User(username="@"+TELEGRAM_ADMIN_USERNAME))
    application.add_handler(vote_handler)

    vote_process_handler = MessageHandler(
                filters.User(username="@"+TELEGRAM_ADMIN_USERNAME)
                & filters.TEXT
                & (~filters.COMMAND),
            vote_process)
    application.add_handler(vote_process_handler)

    application.run_polling()
