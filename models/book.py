from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

# For creating a book (without id and rating)
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    price: float = Field(..., ge=0.0)
    tags: List[str]
    published_year: int = Field(..., ge=1000, le=9999)
    isbn: str

# For updating a book (all fields optional)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.0)
    tags: Optional[List[str]] = None
    published_year: Optional[int] = Field(None, ge=1000, le=9999)
    isbn: Optional[str] = None

# For returning a complete book object (with id and rating)
class Book(BookCreate):
    id: str
    rating: float = 0.0

# For pagination response
class PaginatedBooks(BaseModel):
    total: int
    page: int
    page_size: int
    books: List[Book]