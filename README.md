# 📚 Alonzo Books API
A RESTful Bookstore API built with **FastAPI**, designed to perform CRUD operations on books, authors, genres, and reviews.

## 🔧 Features
- Add, update, delete, and view books
- Manage authors and genres
- Search books by title
- Add and fetch reviews for books
- Interactive Swagger UI for easy testing

## 🛠️ Tech Stack
- **Python**
- **FastAPI**
- **SQLAlchemy** (ORM)
- **SQLite** (Database)
- **Pydantic** (Validation)
- **Uvicorn** (ASGI server)

## 🚀 How to Run
1. Clone the repository: git clone https://github.com/NaseraThabassum/alonzo_books.git
   cd alonzo_books
2. Create a virtual environment and activate it: python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install the required packages: pip install -r requirements.txt
4. Run the FastAPI server: uvicorn main:app --reload
5. Visit your browser: http://127.0.0.1:8000/docs
