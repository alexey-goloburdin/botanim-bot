import asyncio
from datetime import datetime 
import os

import logging
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters

import config
from books import (
    get_all_books,
    get_already_read_books,
    get_now_reading_book
)
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
        await asyncio.sleep(0.3)


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
    now_read_books = await get_now_reading_book()
    response = "Сейчас мы читаем:\n\n"
    just_one_book = len(now_read_books) == 1
    for index, book in enumerate(now_read_books, 1):
        response += (f"{str(index) + '. ' if not just_one_book else ''}"
                     f"{book.name} "
                     f"(с {book.read_start} по {book.read_finish})\n")
    await context.bot.send_message(
            chat_id=effective_chat.id,
            text=response)


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

    application.run_polling()
