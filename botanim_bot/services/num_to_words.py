def num_to_words(count: int, word_forms: tuple[str, str, str]) -> str:
    if count % 10 == 1 and count % 100 != 11:
        p = 0
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        p = 1
    else:
        p = 2

    return word_forms[p]
