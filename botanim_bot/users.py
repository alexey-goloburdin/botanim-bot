import aiosqlite

import config


async def insert_user(telegram_user_id: int) -> None:
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO bot_user (telegram_id) VALUES (:telegram_id)",
            {"telegram_id": telegram_user_id},
        )
        await db.commit()
