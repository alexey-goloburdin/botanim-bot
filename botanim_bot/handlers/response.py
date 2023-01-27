from typing import cast

import telegram
from telegram import Chat, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def _get_chat_id(update: Update) -> int | str:
    return cast(Chat, update.effective_chat).id


async def send_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    await context.bot.send_message(
        chat_id=_get_chat_id(update),
        text=response,
        reply_markup=keyboard,
        parse_mode=telegram.constants.ParseMode.HTML,
    )
