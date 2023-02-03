from typing import cast
from telegram import Update, User
from telegram.ext import ContextTypes

from botanim_bot.handlers.response import send_response
from botanim_bot.services.vote_results import (
    get_leaders,
)
from botanim_bot.services.votings import get_user_vote
from botanim_bot.templates import render_template


async def vote_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = await get_leaders()
    if leaders is None:
        await send_response(
            update, context, response=render_template("vote_results_no_data.j2")
        )
        return

    your_vote = await get_user_vote(
        cast(User, update.effective_user).id, leaders.voting.id
    )
    await send_response(
        update,
        context,
        response=render_template(
            "vote_results.j2", {"leaders": leaders, "your_vote": your_vote}
        ),
    )
