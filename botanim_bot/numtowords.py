from num2words.lang_RU import Num2Word_RU

def books2words(book_num: int) -> str:
    num_to_words = Num2Word_RU._int2word(Num2Word_RU(), book_num, feminine=True) + " книг"
    if book_num == 1:
        num_to_words += "а"
    elif 1 < book_num < 5:
        num_to_words += "и"
    return num_to_words

