import logging
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from botanim_bot.db import close_db

from botanim_bot import config
from botanim_bot import handlers


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_BOTANIM_CHANNEL_ID:
    exit("Specify TELEGRAM_BOT_TOKEN and TELEGRAM_BOTANIM_CHANNEL_ID env variables")


def main():
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_))

    application.add_handler(CommandHandler("allbooks", handlers.all_books))
    application.add_handler(
        CallbackQueryHandler(
            handlers.all_books_button,
            pattern=rf"^{config.ALL_BOOKS_CALLBACK_PATTERN}(\d+)$",
        )
    )

    application.add_handler(CommandHandler("already", handlers.already))

    application.add_handler(CommandHandler("now", handlers.now))

    application.add_handler(CommandHandler("vote", handlers.vote))
    application.add_handler(CommandHandler("cancel", handlers.cancel))
    application.add_handler(
        CallbackQueryHandler(
            handlers.vote_button,
            pattern=rf"^{config.VOTE_BOOKS_CALLBACK_PATTERN}(\d+)$",
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


try:
    main()
except Exception:
    import traceback

    logger.warning(traceback.format_exc())
finally:
    close_db()
