# app/models.py
from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    service_id: str = Field(..., example="64a1f0ef1234567890abcdef")
    reviewer_id: str = Field(..., example="60d9f9f3e1dfe73b8c2f9abc")
    rating: int        = Field(..., ge=1, le=5, example=5)
    comment: Optional[str] = Field(None, example="¡Excelente servicio!")

class ReviewOut(BaseModel):
    id: str
    service_id: str
    reviewer_id: str
    rating: int
    comment: Optional[str]
    created_at: str

    class Config:
        schema_extra = {
            "example": {
                "id":           "64a1f0ef1234567890abcdef",
                "service_id":   "64a1f0ef1234567890abcdef",
                "reviewer_id":  "60d9f9f3e1dfe73b8c2f9abc",
                "rating":       5,
                "comment":      "¡Excelente!",
                "created_at":   "2025-07-19T18:00:00.000000"
            }
        }