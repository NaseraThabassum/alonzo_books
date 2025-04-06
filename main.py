from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from routers import book_router, reviews

# Initialize data files if they don't exist
def initialize_data_files():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    books_file = os.path.join(data_dir, "books.json")
    if not os.path.exists(books_file):
        with open(books_file, "w") as f:
            json.dump([], f)
    
    reviews_file = os.path.join(data_dir, "reviews.json")
    if not os.path.exists(reviews_file):
        with open(reviews_file, "w") as f:
            json.dump([], f)

initialize_data_files()

app = FastAPI(
    title="Alonzo Books API",
    description="A RESTful API for a mock online bookstore",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(book_router.router, tags=["Books"])
app.include_router(reviews.router, tags=["Reviews"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Alonzo Books API. Visit /docs for the API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)