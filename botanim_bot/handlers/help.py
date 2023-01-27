from telegram import Update
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot import message_texts


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_response(update, context, message_texts.HELP)
