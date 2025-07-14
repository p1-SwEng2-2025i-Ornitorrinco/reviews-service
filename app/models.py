from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        """
        Pydantic v2 llama a validate con (cls, v, info).
        Hacemos info opcional para compatibilidad.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {'type': 'string', 'pattern': '^[0-9a-fA-F]{24}$'}


class ReviewCreate(BaseModel):
    service_id: PyObjectId = Field(..., alias="service_id")
    reviewer_id: PyObjectId = Field(..., alias="reviewer_id")
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

    class Config:
        validate_by_name = True
        json_encoders = {ObjectId: str}

class ReviewOut(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    service_id: PyObjectId
    reviewer_id: PyObjectId
    rating: int
    comment: Optional[str]
    created_at: datetime        # ← aquí

    model_config = ConfigDict(
        validate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "60d9f9f3e1dfe73b8c2f9abc",
                "service_id": "684ca91a36e9e6c9b9eb1f63",
                "reviewer_id": "60d9f9f3e1dfe73b8c2f9abd",
                "rating": 5,
                "comment": "¡Excelente!",
                "created_at": "2025-07-14T17:30:00.000Z"
            }
        }
    )
