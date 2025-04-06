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
    "title": "Test Book",
    "author": "Test Author",
    "genre": "Test Genre",
    "price": 19.99,
    "tags": ["test", "sample"],
    "published_year": 2023,
    "isbn": "1234567890123"
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
    
    yield
    
    # Restore backup files
    for file in ["books.json", "reviews.json"]:
        if os.path.exists(f"data/{file}"):
            os.remove(f"data/{file}")
        if os.path.exists(f"data/{file}.bak"):
            os.rename(f"data/{file}.bak", f"data/{file}")

def test_create_book(setup_test_data):
    response = client.post("/books", json=test_book)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_book["title"]
    assert "id" in data
    assert data["rating"] == 0.0

def test_get_book(setup_test_data):
    # First create a book
    create_response = client.post("/books", json=test_book)
    book_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_book["title"]
    assert data["id"] == book_id

def test_update_book(setup_test_data):
    # First create a book
    create_response = client.post("/books", json=test_book)
    book_id = create_response.json()["id"]
    
    # Then update it
    update_data = {"title": "Updated Title", "price": 29.99}
    response = client.put(f"/books/{book_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["price"] == 29.99
    assert data["author"] == test_book["author"]  # Unchanged fields remain

def test_delete_book(setup_test_data):
    # First create a book
    create_response = client.post("/books", json=test_book)
    book_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404

def test_list_books(setup_test_data):
    # Create multiple books
    for i in range(3):
        book = test_book.copy()
        book["title"] = f"Test Book {i}"
        client.post("/books", json=book)
    
    # Get list of books
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["books"]) == 3
    
    # Test pagination
    response = client.get("/books?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["books"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2

def test_search_books(setup_test_data):
    # Create books with different attributes
    books = [
        {**test_book, "title": "Python Programming", "author": "John Smith", "price": 29.99, "genre": "Programming"},
        {**test_book, "title": "Web Development", "author": "Jane Doe", "price": 39.99, "genre": "Programming"},
        {**test_book, "title": "Fantasy Novel", "author": "Sarah Johnson", "price": 19.99, "genre": "Fiction"}
    ]
    
    for book in books:
        client.post("/books", json=book)
    
    # Search by author
    response = client.get("/books/search?author=John")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["books"][0]["author"] == "John Smith"
    
    # Search by genre
    response = client.get("/books/search?genre=Programming")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    
    # Search by price range
    response = client.get("/books/search?price_gt=25&price_lt=35")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["books"][0]["price"] == 29.99