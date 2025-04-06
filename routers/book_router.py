from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi import status
from models.book import Book, BookCreate, BookUpdate, PaginatedBooks
from typing import List, Optional
from uuid import uuid4
import json
import os
from collections import defaultdict

router = APIRouter()
DATA_FILE = "data/books.json"
REVIEWS_FILE = "data/reviews.json"

# Utility functions
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

def read_books():
    if not os.path.exists(DATA_FILE):
        logging.error("Books data file not found.")
        return []
    with open(DATA_FILE, "r") as f:
        try:
            books = json.load(f)
            logging.info(f"Loaded {len(books)} books.")
            return books
        except json.JSONDecodeError:
            logging.error("Books data file is malformed.")
            return []



def read_reviews():
    if not os.path.exists(REVIEWS_FILE):
        return []
    with open(REVIEWS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_books(books):
    with open(DATA_FILE, "w") as f:
        json.dump(books, f, indent=4)

def write_reviews(reviews):
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=4)


# GET all books with pagination and sorting
@router.get("/books", response_model=PaginatedBooks)
def get_books(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of books per page"),
    sort_by: Optional[str] = Query(None, description="Sort by field (price, rating, published_year)"),
    sort_desc: bool = Query(False, description="Sort in descending order")
):
    books = read_books()
    
    # Apply sorting if specified
    if sort_by:
        if sort_by not in ["price", "rating", "published_year"]:
            raise HTTPException(status_code=400, detail="Invalid sort field")
        
        books.sort(key=lambda x: x[sort_by], reverse=sort_desc)
    
    # Apply pagination
    total = len(books)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    page_books = books[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "books": page_books
    }

# GET book by ID
@router.get("/books/{book_id}", response_model=Book)
def get_book(book_id: str = Path(..., description="The ID of the book to get")):
    books = read_books()
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

# POST new book
@router.post("/books", response_model=Book, status_code=201)
def add_book(book: BookCreate):
    new_book = book.dict()
    new_book["id"] = str(uuid4())
    new_book["rating"] = 0.0
    
    books = read_books()
    books.append(new_book)
    write_books(books)
    
    return new_book

# PUT update book
@router.put("/books/{book_id}", response_model=Book)
def update_book(
    book_id: str = Path(..., description="The ID of the book to update"),
    updated_book: BookUpdate = Depends()
):
    books = read_books()
    for index, book in enumerate(books):
        if book["id"] == book_id:
            # Update only provided fields
            update_data = updated_book.dict(exclude_unset=True)
            current_book = book.copy()
            current_book.update(update_data)
            books[index] = current_book
            write_books(books)
            return current_book
    
    raise HTTPException(status_code=404, detail="Book not found")

# DELETE book


from fastapi import HTTPException
import traceback  # Optional, for better debugging during development

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str = Path(..., description="The ID of the book to delete")):
    try:
        books = read_books()
        book_exists = any(book["id"] == book_id for book in books)

        if not book_exists:
            raise HTTPException(status_code=404, detail="Book not found")

        # Remove the book
        updated_books = [book for book in books if book["id"] != book_id]
        write_books(updated_books)

        # Also remove associated reviews
        reviews = read_reviews()
        updated_reviews = [review for review in reviews if review.get("book_id") != book_id]
        write_reviews(updated_reviews)

        return None

    except HTTPException:
        raise  # Let FastAPI handle HTTP-level exceptions
    except Exception as e:
        # Optional for logging: print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# GET all genres
@router.get("/genres", response_model=List[str])
def get_genres():
    books = read_books()
    genres = set()
    for book in books:
        genres.add(book["genre"])
    return sorted(list(genres))

# GET all authors
@router.get("/authors", response_model=List[str])
def get_authors():
    books = read_books()
    authors = set()
    for book in books:
        authors.add(book["author"])
    return sorted(list(authors))

# GET search books
# GET search books
@router.get("/books/search", response_model=PaginatedBooks)
def search_books(
    author: Optional[str] = None,
    genre: Optional[str] = None,
    price_lt: Optional[float] = None,
    price_lte: Optional[float] = None,
    price_gt: Optional[float] = None,
    tag: Optional[str] = None,
    published_year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_desc: bool = False
):
    books = read_books()  # Load books using the read_books function
    
    # Apply filters
    filtered_books = books
    
    # Filter by author
    if author:
        filtered_books = [book for book in filtered_books if author.lower() in book["author"].lower()]
    
    # Filter by genre
    if genre:
        filtered_books = [book for book in filtered_books if genre.lower() in book["genre"].lower()]
    
    # Filter by price
    if price_lt:
        filtered_books = [book for book in filtered_books if book["price"] < price_lt]
    if price_lte:
        filtered_books = [book for book in filtered_books if book["price"] <= price_lte]
    if price_gt:
        filtered_books = [book for book in filtered_books if book["price"] > price_gt]
    
    # Filter by tag
    if tag:
        filtered_books = [book for book in filtered_books if tag.lower() in [t.lower() for t in book["tags"]]]
    
    # Filter by published year
    if published_year:
        filtered_books = [book for book in filtered_books if book["published_year"] == published_year]

    # Sorting logic
    if sort_by:
        if sort_by not in ["price", "rating", "published_year"]:
            raise HTTPException(status_code=400, detail="Invalid sort field")
        
        filtered_books.sort(key=lambda x: x[sort_by], reverse=sort_desc)

    # Pagination logic
    total = len(filtered_books)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    paginated_books = filtered_books[start_idx:end_idx]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "books": paginated_books
    }