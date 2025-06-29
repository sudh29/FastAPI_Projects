from fastapi import Body, FastAPI

app: FastAPI = FastAPI()

BOOKS: list[dict[str, str]] = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]


@app.get("/")
def main_page() -> dict[str, str]:
    """
    Root endpoint for the Books API.
    Returns a welcome message.
    """
    return {"message": "Welcome to the Books API!"}


@app.get("/books")
async def read_all_books() -> list[dict[str, str]]:
    """
    Get all books in the collection.
    Returns a list of all book dictionaries.
    """
    return BOOKS


@app.get("/books/{book_title}")
async def read_book(book_title: str) -> dict[str, str] | None:
    """
    Get a book by its title.
    Args:
        book_title (str): The title of the book to retrieve.
    Returns:
        dict[str, str] | None: The book dictionary if found, else None.
    """
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book


@app.get("/books/")
async def read_category_by_query(category: str) -> list[dict[str, str]]:
    """
    Get all books in a specific category.
    Args:
        category (str): The category to filter books by.
    Returns:
        list[dict[str, str]]: List of books in the given category.
    """
    books_to_return: list[dict[str, str]] = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/byauthor/")
async def read_books_by_author_path(author: str) -> list[dict[str, str]]:
    """
    Get all books by a specific author.
    Args:
        author (str): The author to filter books by.
    Returns:
        list[dict[str, str]]: List of books by the given author.
    """
    books_to_return: list[dict[str, str]] = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_author}/")
async def read_author_category_by_query(
    book_author: str, category: str
) -> list[dict[str, str]]:
    """
    Get all books by a specific author and category.
    Args:
        book_author (str): The author to filter books by.
        category (str): The category to filter books by.
    Returns:
        list[dict[str, str]]: List of books by the given author and category.
    """
    books_to_return: list[dict[str, str]] = []
    for book in BOOKS:
        if (
            book.get("author").casefold() == book_author.casefold()
            and book.get("category").casefold() == category.casefold()
        ):
            books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book: dict = Body()) -> None:
    """
    Add a new book to the collection.
    Args:
        new_book (dict): The book dictionary to add.
    """
    BOOKS.append(new_book)


@app.put("/books/update_book")
async def update_book(updated_book: dict = Body()) -> None:
    """
    Update an existing book in the collection by title.
    Args:
        updated_book (dict): The updated book dictionary.
    """
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str) -> None:
    """
    Delete a book from the collection by title.
    Args:
        book_title (str): The title of the book to delete.
    """
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
