DAYS = ("книга", "книги", "книг")


def books_to_words(books_count: int) -> str:
    penultimate_digit, last_digit = _get_last_two_digits(books_count)

    if penultimate_digit == 1:
        index = 2
    else:
        if last_digit == 1:
            index = 0
        elif last_digit in (2, 3, 4):
            index = 1
        else:
            index = 2

    return DAYS[index]


def _get_last_two_digits(number: int) -> tuple[int, int]:
    list_of_digits = list(str(number))
    if len(list_of_digits) == 1:
        return 0, number

    return int(list_of_digits[-2]), int(list_of_digits[-1])