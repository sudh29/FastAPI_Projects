from typing import Optional, List
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app: FastAPI = FastAPI()


class Book(BaseModel):
    """
    Represents a book with its details.
    """

    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int


class BookRequest(BaseModel):
    """
    Pydantic model for book creation and update requests.
    """

    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2029,
            }
        }
    }


BOOKS: List[Book] = [
    Book(
        id=1,
        title="Computer Science Pro",
        author="codingwithroby",
        description="A very nice book!",
        rating=5,
        published_date=2030,
    ),
    Book(
        id=2,
        title="Be Fast with FastAPI",
        author="codingwithroby",
        description="A great book!",
        rating=5,
        published_date=2030,
    ),
    Book(
        id=3,
        title="Master Endpoints",
        author="codingwithroby",
        description="A awesome book!",
        rating=5,
        published_date=2029,
    ),
    Book(
        id=4,
        title="HP1",
        author="Author 1",
        description="Book Description",
        rating=2,
        published_date=2028,
    ),
    Book(
        id=5,
        title="HP2",
        author="Author 2",
        description="Book Description",
        rating=3,
        published_date=2027,
    ),
    Book(
        id=6,
        title="HP3",
        author="Author 3",
        description="Book Description",
        rating=1,
        published_date=2026,
    ),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books() -> List[Book]:
    """
    Get all books in the collection.
    Returns:
        list[Book]: List of all books.
    """
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)) -> Book:
    """
    Get a book by its ID.
    Args:
        book_id (int): The ID of the book to retrieve.
    Returns:
        Book: The book with the given ID.
    Raises:
        HTTPException: If the book is not found.
    """
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)) -> List[Book]:
    """
    Get all books with a specific rating.
    Args:
        book_rating (int): The rating to filter books by.
    Returns:
        list[Book]: List of books with the given rating.
    """
    books_to_return: List[Book] = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(
    published_date: int = Query(gt=1999, lt=2031),
) -> List[Book]:
    """
    Get all books published in a specific year.
    Args:
        published_date (int): The year to filter books by.
    Returns:
        list[Book]: List of books published in the given year.
    """
    books_to_return: List[Book] = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest) -> None:
    """
    Create a new book and add it to the collection.
    Args:
        book_request (BookRequest): The book data to create.
    """
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book) -> Book:
    """
    Assign a new ID to the book based on the last book in the collection.
    Args:
        book (Book): The book to assign an ID to.
    Returns:
        Book: The book with the assigned ID.
    """
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest) -> None:
    """
    Update an existing book in the collection.
    Args:
        book (BookRequest): The updated book data.
    Raises:
        HTTPException: If the book is not found.
    """
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)) -> None:
    """
    Delete a book from the collection by ID.
    Args:
        book_id (int): The ID of the book to delete.
    Raises:
        HTTPException: If the book is not found.
    """
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")
