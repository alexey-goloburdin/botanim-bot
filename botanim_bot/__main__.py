import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    Defaults,
    MessageHandler,
    filters,
)

from botanim_bot import config, handlers
from botanim_bot.db import close_db

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_,
    "allbooks": handlers.all_books,
    "already": handlers.already,
    "now": handlers.now,
    "vote": handlers.vote,
    "cancel": handlers.cancel,
    "voteresults": handlers.vote_results,
}

CALLBACK_QUERY_HANDLERS = {
    rf"^{config.ALL_BOOKS_CALLBACK_PATTERN}(\d+)$": handlers.all_books_button,
    rf"^{config.VOTE_BOOKS_CALLBACK_PATTERN}(\d+)$": handlers.vote_button,
}


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_BOTANIM_CHANNEL_ID:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN and TELEGRAM_BOTANIM_CHANNEL_ID env variables "
        "wasn't implemented in .env (both should be initialized)."
    )


def main():
    application = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .defaults(defaults=Defaults(block=False))
        .build()
    )

    for command_name, command_handler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_handler))

    for pattern, handler in CALLBACK_QUERY_HANDLERS.items():
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.vote_process)
    )

    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        logger.warning(traceback.format_exc())
    finally:
        close_db()
