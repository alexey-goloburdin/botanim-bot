from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import LiteralString

import aiosqlite

import config


@dataclass
class Book:
    id: int
    name: str
    category_id: int
    category_name: str
    read_start: str | None
    read_finish: str | None

    def __post_init__(self):
        """Set up read_start and read_finish to needed string format"""
        for field in ("read_start", "read_finish"):
            value = getattr(self, field)
            if value is None:
                continue
            value = datetime.strptime(value, "%Y-%m-%d").strftime(config.DATE_FORMAT)
            setattr(self, field, value)


@dataclass
class Category:
    id: int
    name: str
    books: Iterable[Book]


def _format_book_name(book_name_with_author: str) -> str:
    try:
        book_name, author = tuple(map(str.strip, book_name_with_author.split("::")))
    except ValueError:
        print(book_name_with_author)
        return book_name_with_author
    return f"{book_name}. <i>{author}</i>"


def build_category_with_books_string(category: Category) -> str:
    response = ["<b>" + category.name + "</b>\n\n"]
    for _, book in enumerate(category.books, 1):
        response.append(f"◦ {_format_book_name(book.name)}\n")
    return "".join(response)


async def get_all_books() -> Iterable[Category]:
    sql = (
        _get_books_base_sql()
        + """
        ORDER BY c."ordering", b."ordering" """
    )
    books = await _get_books_from_db(sql)
    return _group_books_by_categories(books)


async def get_not_started_books() -> Iterable[Category]:
    sql = (
        _get_books_base_sql()
        + """
        WHERE b.read_start IS NULL
        ORDER BY c."ordering", b."ordering" """
    )
    books = await _get_books_from_db(sql)
    return _group_books_by_categories(books)


async def get_already_read_books() -> Iterable[Book]:
    sql = (
        _get_books_base_sql()
        + """
        WHERE read_start<current_date
            AND read_finish  <= current_date
        ORDER BY b.read_start"""
    )
    return await _get_books_from_db(sql)


async def get_now_reading_books() -> Iterable[Book]:
    sql = (
        _get_books_base_sql()
        + """
        WHERE read_start<=current_date
            AND read_finish>=current_date
        ORDER BY b.read_start"""
    )
    return await _get_books_from_db(sql)


async def get_books_by_numbers(numbers: Iterable[int]) -> Iterable[Book]:
    numbers_joined = ", ".join(map(str, map(int, numbers)))

    hardcoded_sql_values = []
    for index, number in enumerate(numbers, 1):
        hardcoded_sql_values.append(f"({number}, {index})")
    hardcoded_sql_values = ", ".join(hardcoded_sql_values)

    base_sql = _get_books_base_sql(
        'ROW_NUMBER() over (order by c."ordering", b."ordering") as idx'
    )
    sql = f"""
        SELECT t2.* FROM (
          VALUES {hardcoded_sql_values}
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
    books = await _get_books_from_db(sql)
    return books


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
            b.read_start, b.read_finish
        FROM book b
        LEFT JOIN book_category c ON c.id=b.category_id
    """


async def _get_books_from_db(sql: LiteralString) -> Iterable[Book]:
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                books.append(
                    Book(
                        id=row["book_id"],
                        name=row["book_name"],
                        category_id=row["category_id"],
                        category_name=row["category_name"],
                        read_start=row["read_start"],
                        read_finish=row["read_finish"],
                    )
                )
    return books
