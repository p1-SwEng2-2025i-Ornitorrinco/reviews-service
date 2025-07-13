from datetime import datetime
from pydantic import BaseModel, Field
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
    created_at: datetime

    class Config:
        validate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
