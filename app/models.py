# app/models.py
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Helper para validar ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

# Schema de creación (entrada)
class ReviewCreate(BaseModel):
    service_id: PyObjectId = Field(..., alias="service_id")
    reviewer_id: PyObjectId = Field(..., alias="reviewer_id")
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

# Schema para respuesta (salida)
class ReviewOut(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    service_id: PyObjectId
    reviewer_id: PyObjectId
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
