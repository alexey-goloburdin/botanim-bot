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
    category_id: int
    dateTime: str
    name: str
    payment_type: int
    price: int
    custom_comment: str
    category_name: int


@dataclass
class Category:
    id: int
    name: str
    books: list[Book]


async def get_all_books() -> Iterable[Category]:
    sql = f"""{_get_books_base_sql()}
              ORDER BY c."ordering", b."ordering" """
    books = await _get_books_from_db(sql)
    return _group_books_by_categories(books)


async def get_not_started_books() -> Iterable[Category]:
    sql = f"""{_get_books_base_sql()}
              WHERE b.read_start IS NULL
              ORDER BY c."ordering", b."ordering" """
    books = await _get_books_from_db(sql)
    return _group_books_by_categories(books)


async def get_already_read_books() -> Iterable[Book]:
    sql = f"""{_get_books_base_sql()}
              WHERE read_start<current_date
                  AND read_finish  <= current_date
              ORDER BY b.read_start"""
    return await _get_books_from_db(sql)


async def get_now_reading_books() -> Iterable[Book]:
    sql = f"""{_get_books_base_sql()}
              WHERE read_start<=current_date
                  AND read_finish>=current_date
              ORDER BY b.read_start"""
    return await _get_books_from_db(sql)


async def get_next_book() -> Book | None:
    sql = f"""{_get_books_base_sql()}
              WHERE b.read_start > current_date
              ORDER BY b.read_start
              LIMIT 1"""
    books = await _get_books_from_db(sql)
    if not books:
        return None
    return books[0]


def calculate_category_books_start_index(
    categories: Iterable[Category], current_category: Category
) -> int | None:
    start_index = 0
    for category in categories:
        if category.id != current_category.id:
            start_index += len(tuple(category.books))
        else:
            break

    return start_index


async def get_books_by_positional_numbers(numbers: Iterable[int]) -> tuple[Book]:
    numbers_joined = ", ".join(map(str, map(int, numbers)))

    hardcoded_sql_values = []
    for index, number in enumerate(numbers, 1):
        hardcoded_sql_values.append(f"({number}, {index})")

    output_hardcoded_sql_values = ", ".join(hardcoded_sql_values)

    base_sql = _get_books_base_sql(
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
    return tuple(await _get_books_from_db(cast(LiteralString, sql)))


async def get_book_names_by_ids(ids: Iterable[int]) -> dict[int, str]:
    int_ids = tuple(map(str, map(int, ids)))
    sql = f"""{_get_books_base_sql()}
              WHERE b.id IN ({",".join(int_ids)})
              ORDER BY c."name", b."name" """
    books = await _get_books_from_db(cast(LiteralString, sql))
    return {book.id: book.name for book in books}


def format_book_name(book_name: str) -> str:
    try:
        book_name, author = tuple(map(str.strip, book_name.split("::")))
    except ValueError:
        return book_name
    return f"{book_name}. <i>{author}</i>"


def _group_books_by_categories(books: Iterable[Book]) -> Iterable[Category]:
    categories = []
    category_id = None
    for book in books:
        if category_id != book.category_id:
            categories.append(
                Category(id=book.category_id, name=book.category_name, books=[book])
            )
            category_id = book.category_id
            continue
        categories[-1].books.append(book)
    return categories


def _get_books_base_sql(select_param: LiteralString | None = None) -> LiteralString:
    return f"""
        SELECT
            b.id as book_id,
            b.name as book_name,
            c.id as category_id,
            c.name as category_name,
            {select_param + "," if select_param else ""}
            b.read_start, b.read_finish,
            read_comments
        FROM book b
        LEFT JOIN book_category c ON c.id=b.category_id
    """


async def _get_books_from_db(sql: LiteralString) -> list[Book]:
    books_raw = await fetch_all(sql)
    return [
        Book(
            id=book["book_id"],
            name=book["book_name"],
            category_id=book["category_id"],
            category_name=book["category_name"],
            read_start=book["read_start"],
            read_finish=book["read_finish"],
            read_comments=book["read_comments"],
        )
        for book in books_raw
    ]
