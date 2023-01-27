from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts
from botanim_bot.services.vote_mode import remove_user_from_vote_mode


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await remove_user_from_vote_mode(cast(User, update.effective_user).id)
    await send_response(update, context, message_texts.GREETINGS)
