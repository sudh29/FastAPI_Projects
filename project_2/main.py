from typing import Optional, List
from fastapi import FastAPI, Path, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette import status

app: FastAPI = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books(
    rating: Optional[int] = Query(None, gt=0, lt=6),
    published_date: Optional[int] = Query(None, gt=1999, lt=2031),
) -> List[Book]:
    """
    Get all books in the collection, optionally filtered by rating or published date.
    """
    books_to_return = BOOKS

    if rating is not None:
        books_to_return = [book for book in books_to_return if book.rating == rating]

    if published_date is not None:
        books_to_return = [
            book for book in books_to_return if book.published_date == published_date
        ]

    return books_to_return


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)) -> Book:
    """
    Get a book by its ID.
    """
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest) -> Book:
    """
    Create a new book and add it to the collection.
    """
    new_book = Book(**book_request.model_dump())
    new_book = find_book_id(new_book)
    BOOKS.append(new_book)
    return new_book


def find_book_id(book: Book) -> Book:
    """
    Assign a new ID to the book based on the last book in the collection.
    """
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest) -> None:
    """
    Update an existing book in the collection.
    """
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            # Create a new Book instance with the updated data
            # We assume book_request contains all necessary fields
            BOOKS[i] = Book(
                id=book_request.id,
                title=book_request.title,
                author=book_request.author,
                description=book_request.description,
                rating=book_request.rating,
                published_date=book_request.published_date,
            )
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)) -> None:
    """
    Delete a book from the collection by ID.
    """
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
