import logging
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from . import config
from . import handlers


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


if not config.TELEGRAM_BOT_TOKEN:
    exit("Specify TELEGRAM_BOT_TOKEN env variable")


def main():
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_))

    application.add_handler(CommandHandler("allbooks", handlers.all_books))
    application.add_handler(
        CallbackQueryHandler(
            handlers.all_books_button,
            pattern="^" + config.ALL_BOOKS_CALLBACK_PATTERN + r"(\d+)$",
        )
    )

    application.add_handler(CommandHandler("already", handlers.already))

    application.add_handler(CommandHandler("now", handlers.now))

    application.add_handler(CommandHandler("vote", handlers.vote))
    application.add_handler(
        CallbackQueryHandler(
            handlers.vote_button,
            pattern="^" + config.VOTE_BOOKS_CALLBACK_PATTERN + r"(\d+)$",
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            handlers.vote_process,
        )
    )

    application.add_handler(CommandHandler("voteresults", handlers.vote_results))

    application.run_polling()
