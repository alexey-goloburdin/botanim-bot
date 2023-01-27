from botanim_bot.db import execute, fetch_one


async def is_user_in_vote_mode(user_id: int) -> bool:
    user_exists = await fetch_one(
        "select user_id from bot_user_in_vote_mode where user_id=:user_id",
        {"user_id": user_id},
    )
    return user_exists is not None


async def set_user_in_vote_mode(user_id: int) -> None:
    await execute(
        "insert or ignore into bot_user_in_vote_mode (user_id) values (:user_id)",
        {"user_id": user_id},
    )


async def remove_user_from_vote_mode(user_id: int) -> None:
    await execute(
        "delete from bot_user_in_vote_mode where user_id=:user_id",
        {"user_id": user_id},
        autocommit=False,
    )
