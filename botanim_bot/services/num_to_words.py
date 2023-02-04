def num_to_words(count: int, word_forms: tuple[str, str, str]) -> str:
    if 11 <= count % 100 <= 19:
        p = 2
    elif count % 10 == 1:
        p = 0
    elif 2 <= count % 10 <= 4:
        p = 1
    else:
        p = 2

    return word_forms[p]
