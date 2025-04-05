from fastapi import APIRouter
from models.book import Book

router = APIRouter()

# In-memory fake DB
books = []

@router.get("/books")
def get_books():
    return books

@router.post("/books")
def add_book(book: Book):
    books.append(book)
    return {"message": "Book added successfully!"}

@router.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book.id == book_id:
            return book
    return {"error": "Book not found"}

@router.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book.id == book_id:
            del books[index]
            return {"message": "Book deleted successfully!"}
    return {"error": "Book not found"}