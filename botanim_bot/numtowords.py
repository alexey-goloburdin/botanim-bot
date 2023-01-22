from num2words.lang_RU import Num2Word_RU

def books2words(book_num: int) -> str:
    if book_num == 1:
        return "одну книгу"
    num_to_words = Num2Word_RU._int2word(Num2Word_RU(), book_num, feminine=True) + " книг"
    if 1 < book_num < 5:
        num_to_words += "и"
    return num_to_words

