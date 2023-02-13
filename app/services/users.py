from botanim_bot.db import execute


async def insert_user(telegram_user_id: int) -> None:
    await execute(
        "INSERT OR IGNORE INTO bot_user (telegram_id) VALUES (:telegram_id)",
        {"telegram_id": telegram_user_id},
    )
