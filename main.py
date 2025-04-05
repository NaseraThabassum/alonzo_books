from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Alonzo Books API!"}
from routers import books
app.include_router(books.router)