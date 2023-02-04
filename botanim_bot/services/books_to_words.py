DAYS = ["книга", "книги", "книг"]

NOMINATIVE_CASE = [1]
GENITIVE_SINGULAR_CASE = [2, 3, 4]
SPECIAL_NUMBERS = list(range(11, 20))


def books_to_words(books_count: int) -> str:
    remainder_10 = books_count % 10
    remainder_100 = books_count % 100

    if remainder_100 in SPECIAL_NUMBERS:
        return DAYS[2]
    else:
        if remainder_10 in NOMINATIVE_CASE:
            return DAYS[0]
        elif remainder_10 in GENITIVE_SINGULAR_CASE:
            return DAYS[1]
        else:
            return DAYS[2]
