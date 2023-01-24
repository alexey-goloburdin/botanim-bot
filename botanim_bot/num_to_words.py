def books_to_words(books_count: int) -> str:
    books_count = books_count % 100
    last = books_count % 10
    
    return {
        4 < last < 10 or last == 0 or 10 < books_count < 20: "книг",
        1 < last < 5: "книги",
        last == 1 and books_count != 11: "книгу"
        }[True]
    

if __name__ == "__main__":
    for num in (1, 2, 5, 10, 11, 19, 20, 21, 121, 125):
        print(f"{num=}, {books_to_words(num)}")
