from contextlib import contextmanager


@contextmanager
def open_book(book_name):
    print(f"Opening {book_name}...")
    yield
    print(f"Closing {book_name}...")


with open_book("Harry Potter"):
    print("Reading the book...")
