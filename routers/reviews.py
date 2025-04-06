from fastapi import APIRouter, HTTPException, Path, Query
from models.review import Review, ReviewCreate
from typing import List
from uuid import uuid4, UUID
import json
import os

router = APIRouter()
BOOKS_FILE = "data/books.json"
REVIEWS_FILE = "data/reviews.json"

def load_reviews():
    if not os.path.exists(REVIEWS_FILE):
        return []
    with open(REVIEWS_FILE, "r") as file:
        return json.load(file)

def save_reviews(reviews):
    with open(REVIEWS_FILE, "w") as file:
        json.dump(reviews, file, indent=4)

def load_books():
    if not os.path.exists(BOOKS_FILE):
        return []
    with open(BOOKS_FILE, "r") as file:
        return json.load(file)

def save_books(books):
    with open(BOOKS_FILE, "w") as file:
        json.dump(books, file, indent=4)

def recalculate_book_rating(book_id: str):
    reviews = load_reviews()
    book_reviews = [r for r in reviews if r["book_id"] == book_id]
    
    if book_reviews:
        avg_rating = sum([r["rating"] for r in book_reviews]) / len(book_reviews)
    else:
        avg_rating = 0.0
    
    books = load_books()
    for book in books:
        if book["id"] == book_id:
            book["rating"] = round(avg_rating, 2)
            break
    
    save_books(books)

@router.post("/books/{book_id}/reviews", status_code=201, response_model=Review)
def add_review(
    review_data: ReviewCreate,
    book_id: str = Path(..., description="The ID of the book to review")
):
    books = load_books()
    if not any(book["id"] == book_id for book in books):
        raise HTTPException(status_code=404, detail="Book not found")
    
    reviews = load_reviews()
    
    # Create new review with UUID
    new_review = {
        "id": str(uuid4()),
        "book_id": book_id,
        "reviewer": review_data.reviewer,
        "rating": review_data.rating,
        "comment": review_data.comment
    }
    
    reviews.append(new_review)
    save_reviews(reviews)
    
    # Update book rating
    recalculate_book_rating(book_id)
    
    return new_review

@router.get("/books/{book_id}/reviews", response_model=List[Review])
def get_reviews(
    book_id: str = Path(..., description="The ID of the book to get reviews for"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    books = load_books()
    if not any(book["id"] == book_id for book in books):
        raise HTTPException(status_code=404, detail="Book not found")
    
    reviews = load_reviews()
    book_reviews = [r for r in reviews if r["book_id"] == book_id]
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(book_reviews))
    
    return book_reviews[start_idx:end_idx]

@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: str = Path(..., description="The ID of the review to delete")):
    reviews = load_reviews()
    
    review = None
    for r in reviews:
        if r["id"] == review_id:
            review = r
            break
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    book_id = review["book_id"]
    reviews.remove(review)
    save_reviews(reviews)
    
    # Update book rating
    recalculate_book_rating(book_id)
    
    return None  # 204 No Content