DAYS = ("книга", "книги", "книг")


def books_to_words(books_count: int) -> str:
    if 11 <= books_count % 100 <= 19:
        p = 2
    elif books_count % 10 == 1:
        p = 0
    elif 2 <= books_count % 10 <= 4:
        p = 1
    else:
        p = 2

    return DAYS[p]
