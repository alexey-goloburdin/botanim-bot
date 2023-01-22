def books_to_words(books_count: int) -> str:
    match books_count:
        case 1:
            return "одна книга"
        case 2 | 3 | 4:
            return f"{books_count} книги"
        case _:
            return f"{books_count} книг"
