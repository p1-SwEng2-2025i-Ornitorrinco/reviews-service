# app/models.py (ACTUALIZADO)
from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    service_id: str = Field(..., example="64a1f0ef1234567890abcdef")
    reviewer_id: str = Field(..., example="60d9f9f3e1dfe73b8c2f9abc")
    rating: int = Field(..., ge=1, le=5, example=5)
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
                "id": "64a1f0ef1234567890abcdef",
                "service_id": "64a1f0ef1234567890abcdef",
                "reviewer_id": "60d9f9f3e1dfe73b8c2f9abc",
                "rating": 5,
                "comment": "¡Excelente!",
                "created_at": "2025-07-19T18:00:00.000000"
            }
        }

class ReviewWithUserInfo(ReviewOut):
    """
    Modelo de Review que incluye información del usuario que hizo la review
    """
    reviewer_name: Optional[str] = Field(None, description="Nombre completo del reviewer")
    reviewer_photo: Optional[str] = Field(None, description="URL de la foto del reviewer")

    class Config:
        schema_extra = {
            "example": {
                "id": "64a1f0ef1234567890abcdef",
                "service_id": "64a1f0ef1234567890abcdef",
                "reviewer_id": "60d9f9f3e1dfe73b8c2f9abc",
                "rating": 5,
                "comment": "¡Excelente servicio!",
                "created_at": "2025-07-19T18:00:00.000000",
                "reviewer_name": "Juan Pérez",
                "reviewer_photo": "/static/perfiles/juan_foto.jpg"
            }
        }

class ServiceReviewStats(BaseModel):
    """
    Estadísticas de reviews de un servicio
    """
    total_reviews: int
    average_rating: float
    rating_distribution: dict[int, int]

    class Config:
        schema_extra = {
            "example": {
                "total_reviews": 10,
                "average_rating": 4.2,
                "rating_distribution": {
                    1: 0,
                    2: 1,
                    3: 2,
                    4: 3,
                    5: 4
                }
            }
        }