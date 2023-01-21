from dataclasses import dataclass
from datetime import datetime

import aiosqlite

import config



@dataclass
class Book:
    id: int
    name: str
    category_id: int
    category_name: str
    read_start: datetime
    read_finish: datetime


@dataclass
class Category:
    id: int
    name: str
    books: list[Book]


def _group_books_by_categories(books: list[Book]) -> list[Category]:
    categories = []
    category_id = None
    for book in books:
        if category_id != book.category_id:
            categories.append(Category(
                id=book.category_id,
                name=book.category_name,
                books=[book])
            )
            category_id = book.category_id
            continue
        categories[-1].books.append(book)
    return categories


async def get_all_books() -> list[Category]:
    sql = """
        SELECT
            b.id as book_id,
                b.name AS book_name,
                c.id AS category_id,
                c.name AS category_name,
                b.read_start, b.read_finish
        FROM book as b
        LEFT JOIN book_category c ON c.id=b.category_id
        ORDER BY c."ordering", b."ordering" """
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                books.append(Book(
                    id=row["book_id"],
                    name=row["book_name"],
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    read_start=row["read_start"],
                    read_finish=row["read_finish"]
                ))
    return _group_books_by_categories(books)


async def get_already_read_books() -> list[Book]:
    sql = """
        SELECT
            b.id as book_id,
            b.name as book_name,
            c.id as category_id,
            c.name as category_name,
            b.read_start, b.read_finish
        FROM book b
        LEFT JOIN book_category c ON c.id=b.category_id
        WHERE read_start<current_date
            AND read_finish  <= current_date"""
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                books.append(Book(
                    id=row["book_id"],
                    name=row["book_name"],
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    read_start=row["read_start"],
                    read_finish=row["read_finish"]
                ))
    return books
