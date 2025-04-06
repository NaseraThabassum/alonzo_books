import sys
import os
import json
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

# Sample book data for testing
test_book = {
    "title": "Test Book for Reviews",
    "author": "Test Author",
    "genre": "Test Genre",
    "price": 19.99,
    "tags": ["test", "sample"],
    "published_year": 2023,
    "isbn": "1234567890123"
}

# Sample review data
test_review = {
    "reviewer": "Test Reviewer",
    "rating": 4,
    "comment": "This is a test review."
}

@pytest.fixture
def setup_test_data():
    """Setup and teardown for test data"""
    # Create test data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Backup existing data files if they exist
    for file in ["books.json", "reviews.json"]:
        if os.path.exists(f"data/{file}"):
            if os.path.exists(f"data/{file}.bak"):
                os.remove(f"data/{file}.bak")
            os.rename(f"data/{file}", f"data/{file}.bak")
    
    # Create empty data files
    with open("data/books.json", "w") as f:
        json.dump([], f)
    with open("data/reviews.json", "w") as f:
        json.dump([], f)
    
    # Create a test book
    response = client.post("/books", json=test_book)
    book_id = response.json()["id"]
    
    yield book_id
    
    # Restore backup files
    for file in ["books.json", "reviews.json"]:
        if os.path.exists(f"data/{file}"):
            os.remove(f"data/{file}")
        if os.path.exists(f"data/{file}.bak"):
            os.rename(f"data/{file}.bak", f"data/{file}")

def test_add_review(setup_test_data):
    book_id = setup_test_data
    
    response = client.post(f"/books/{book_id}/reviews", json=test_review)
    assert response.status_code == 201
    data = response.json()
    assert data["reviewer"] == test_review["reviewer"]
    assert data["rating"] == test_review["rating"]
    assert data["book_id"] == book_id
    
    # Check that book rating was updated
    book_response = client.get(f"/books/{book_id}")
    book_data = book_response.json()
    assert book_data["rating"] == 4.0

def test_get_reviews(setup_test_data):
    book_id = setup_test_data
    
    # Add multiple reviews
    for i in range(3):
        review = test_review.copy()
        review["reviewer"] = f"Reviewer {i}"
        review["rating"] = i + 3  # Ratings 3, 4, 5
        client.post(f"/books/{book_id}/reviews", json=review)
    
    # Get all reviews
    response = client.get(f"/books/{book_id}/reviews")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Check book rating is average of reviews
    book_response = client.get(f"/books/{book_id}")
    book_data = book_response.json()
    assert book_data["rating"] == 4.0  # (3+4+5)/3 = 4.0

def test_delete_review(setup_test_data):
    book_id = setup_test_data
    
    # Add a review
    review_response = client.post(f"/books/{book_id}/reviews", json=test_review)
    review_id = review_response.json()["id"]
    
    # Delete the review
    delete_response = client.delete(f"/reviews/{review_id}")
    assert delete_response.status_code == 204
    
    # Check that the review is gone
    reviews_response = client.get(f"/books/{book_id}/reviews")
    reviews_data = reviews_response.json()
    assert len(reviews_data) == 0
    
    # Check that book rating was reset
    book_response = client.get(f"/books/{book_id}")
    book_data = book_response.json()
    assert book_data["rating"] == 0.0