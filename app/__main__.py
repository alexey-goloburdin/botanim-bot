import logging
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.db import close_db

from app import config
from app.handlers import start as start_hanler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


if not config.TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN env variables "
                     "wasn't implemented in .env (both should be initialized).")


def main():
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    COMMAND_HANDLERS = {
        "start": start_hanler,
    }
    for command_name, command_handler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_handler))

    # CALLBACK_QUERY_HANDLERS = {
    #     rf"^{config.ALL_BOOKS_CALLBACK_PATTERN}(\d+)$": handlers.all_books_button,
    #     rf"^{config.VOTE_BOOKS_CALLBACK_PATTERN}(\d+)$": handlers.vote_button,
    # }
    # for pattern, handler in CALLBACK_QUERY_HANDLERS.items():
    #     application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    # application.add_handler(
    #     MessageHandler(filters.TEXT & (~filters.COMMAND), start_hanler)
    # )

    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        logger.warning(traceback.format_exc())
    finally:
        close_db()
