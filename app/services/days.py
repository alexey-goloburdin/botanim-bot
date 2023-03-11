from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import LiteralString, cast

from botanim_bot import config
from botanim_bot.db import fetch_all

# TODO: refactor - unbind dataclaasses and make SQL-speaaking objects

@dataclass
'''Represents in-day orders on incomes-expenses'''
class Day:
    id: int
    monthNumber: str
    timeStamp: str
    name: str
    paymentType: int
    categoryName: int
    price: int
    customComment: str


# TODO refactor Categories handling
@dataclass
class Category:
    id: int
    name: str
    days: list[Day]


async def getDaysWithinDateFrame(dateStart: str, dateFinish: str) -> Iterable[Category]:
    sql = f"""{_getDaysBaseSql()}
              ORDER BY c."ordering", b."ordering" """
    days = await _getDaysFromDb(sql)
    return _group_days_by_categories(days)


async def getNotStartedDays() -> Iterable[Category]:
    sql = f"""{_getDaysBaseSql()}
              WHERE b.read_start IS NULL
              ORDER BY c."ordering", b."ordering" """
    days = await _getDaysFromDb(sql)
    return _group_days_by_categories(days)


async def getAlreadyReadDays() -> Iterable[Day]:
    sql = f"""{_getDaysBaseSql()}
              WHERE read_start<current_date
                  AND read_finish  <= current_date
              ORDER BY b.read_start"""
    return await _getDaysFromDb(sql)


async def getNowReadingDays() -> Iterable[Day]:
    sql = f"""{_getDaysBaseSql()}
              WHERE read_start<=current_date
                  AND read_finish>=current_date
              ORDER BY b.read_start"""
    return await _getDaysFromDb(sql)


async def getNextDay() -> Day | None:
    sql = f"""{_getDaysBaseSql()}
              WHERE b.read_start > current_date
              ORDER BY b.read_start
              LIMIT 1"""
    days = await _getDaysFromDb(sql)
    if not days:
        return None
    return days[0]


async def get_days_by_positional_numbers(numbers: Iterable[int]) -> tuple[Day]:
    numbers_joined = ", ".join(map(str, map(int, numbers)))

    hardcoded_sql_values = []
    for index, number in enumerate(numbers, 1):
        hardcoded_sql_values.append(f"({number}, {index})")

    output_hardcoded_sql_values = ", ".join(hardcoded_sql_values)

    base_sql = _getDaysBaseSql(
        'ROW_NUMBER() over (order by c."ordering", b."ordering") as idx'
    )
    sql = f"""
        SELECT t2.* FROM (
          VALUES {output_hardcoded_sql_values}
        ) t0
        INNER JOIN
        (
        SELECT t.* FROM (
            {base_sql}
            WHERE read_start IS NULL
        ) t
        WHERE t.idx IN ({numbers_joined})
        ) t2
        ON t0.column1 = t2.idx
        ORDER BY t0.column2
    """
    return tuple(await _getDaysFromDb(cast(LiteralString, sql)))


async def getDaysByPaymentType(paymentType: int) -> dict[int, str]:
    sql = f"""{_getDaysBaseSql()} WHERE payment_type = {paymentType}"""
    days = await _getDaysFromDb(cast(LiteralString, sql))
    return {day for day in days}


def format_day_name(book_name: str) -> str:
    try:
        day_name, author = tuple(map(str.strip, book_name.split("::")))
    except ValueError:
        return day_name
    return f"{day_name}. <i>{author}</i>"


def _groupDaysByCategories(days: Iterable[Day]) -> Iterable[Category]:
    categories = []
    categoryName = ''
    for day in days:
        if categoryName!= day.category_name:
            categories.append(
                Category(name=day.category_name, days=[book])
            )
            categoryName = day.category_name
            continue
        categories[-1].days.append(day)
    return categories


def _getDaysBaseSql(select_param: LiteralString | None = None) -> LiteralString:
    return f"""
        SELECT * FROM days
    """


async def _getDaysFromDb(sql: LiteralString) -> list[Days]:
    daysRaw = await fetch_all(sql)
    return [
        Day(
            id=day["id"],
            monthNumber=day["month_number"],
            timeStamp=day["timeStamp"],
            name=day["name"],
            paymentType=day["payment_type"],
            categoryName=day["category_name"],
            price=day["price"],
            customComment=day["custom_comment"],

        )
        for days in daysRaw
    ]
