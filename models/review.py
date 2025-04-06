from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class Review(BaseModel):
    id: UUID
    book_id: UUID
    reviewer: str
    rating: int = Field(..., ge=1, le=5)  # rating must be between 1 and 5
    comment: str

class ReviewCreate(BaseModel):
    reviewer: str
    rating: int = Field(..., ge=1, le=5)
    comment: str