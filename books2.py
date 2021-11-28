from typing import Optional
from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from pydantic import BaseModel, Field
from uuid import UUID
from starlette.responses import JSONResponse


class NegativeNumberException(Exception):
    def __self__(self, books_to_return):
        self.books_to_return = books_to_return


app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        title="Description of the book", max_length=100, min_length=1)
    rating: int = Field(gt=-1, lt=101)

    class Config:
        schema_extra = {
            "example": {
                "id": "0dde9040-56da-4df4-b4d8-bc8a210e0d79",
                "title": "computer science",
                "author": "gobella",
                "description": "A nice description",
                "rating": 75
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str
    description: Optional[str] = Field(
        None, title="description of the book", max_length=100, min_length=1)


BOOKS = []


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberException):

    return JSONResponse(
        status_code=418,
        content={"message": f"why don you want {exception.books_to_return}"}
    )


@app.post("/books/login")
async def book_login(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password": password}


@app.get("/header")
async def read_header(random_header: Optional[str] = Header(None)):
    return {"Random-Header": random_header}


@app.get("/")
async def read_all_books(books_to_return: Optional[int] = None):

    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return=books_to_return)

    if len(BOOKS) < 1:
        create_books_no_api()

    if books_to_return and len(BOOKS) >= books_to_return > 0:
        i = 1
        new_books = []
        while i <= books_to_return:
            new_books.append(BOOKS[i - 1])
            i += 1
        return new_books

    return BOOKS


@app.get("/book/{book_id}")
async def read_book(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise raise_item_cannot_be_found_exception()


@app.get("/book/rating/{book_id}", response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise raise_item_cannot_be_found_exception()


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    return book


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book):
    counter = 0

    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            BOOKS[counter - 1] = book
            return BOOKS[counter - 1]


@app.delete("/{book_id}")
async def delete_book(book_id: UUID):
    counter = 0

    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            del BOOKS[counter - 1]
            return f"id: {book_id} deleted"

    raise raise_item_cannot_be_found_exception()


def create_books_no_api():
    book_1 = Book(id="0dde9040-56da-4df4-b4d8-bc8a210e0d7d",
                  title="title1",
                  author="gobella",
                  description="descriptino1",
                  rating=60)

    book_2 = Book(id="0dde9040-56da-4df4-b4d8-bc8a210e0d71",
                  title="title2",
                  author="gobella",
                  description="descriptino1",
                  rating=60)

    book_3 = Book(id="0dde9040-56da-4df4-b4d8-bc8a210e0d72",
                  title="title3",
                  author="gobella",
                  description="descriptino1",
                  rating=60)

    book_4 = Book(id="0dde9040-56da-4df4-b4d8-bc8a210e0d73",
                  title="title4",
                  author="gobella",
                  description="descriptino1",
                  rating=60)

    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)


def raise_item_cannot_be_found_exception():
    return HTTPException(status_code=404, detail="book not founded", headers={"X-Header-Error": "not to found"})
