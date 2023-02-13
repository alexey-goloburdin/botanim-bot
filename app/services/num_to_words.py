def books_to_words(books_count: int) -> str:
    days = ["книга", "книги", "книг"]
    if books_count % 10 == 1 and books_count % 100 != 11:
        p = 0
    elif 2 <= books_count % 10 <= 4 and (
        books_count % 100 < 10 or books_count % 100 >= 20
    ):
        p = 1
    else:
        p = 2
    return days[p]
