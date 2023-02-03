import urllib.parse

import httpx

from botanim_bot import config


async def is_user_in_channel(user_id: int, channel_id: int) -> bool:
    """Returns True if user `user_id` in `channel_id` now"""
    url = _get_tg_url(method="getChatMember", chat_id=channel_id, user_id=user_id)
    json_response = await httpx.get(url).json()
    try:
        return json_response["result"]["status"] in (
            "member",
            "creator",
            "administrator",
        )
    except KeyError:
        return False


def _get_tg_url(method: str, **params) -> str:
    """Returns URL for Telegram Bot API method `method`
    and optional key=value `params`"""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return url
