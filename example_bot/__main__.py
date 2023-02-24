import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from example_bot import config, handlers

COMMAND_HANDLERS = {
    "start": handlers.start,
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
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    for command_name, command_handler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_handler))

    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        logger.warning(traceback.format_exc())
    finally:
        logger.warning("shut down")
