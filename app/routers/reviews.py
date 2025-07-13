# app/routers/reviews.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models import ReviewCreate, ReviewOut
from app.crud import (
    insert_review,
    get_review_by_id,
    get_reviews_by_service,
    delete_review_by_id,
    recalc_user_reputation
)

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate):
    # Inserta la reseña
    new_id = await insert_review(review)
    # Recalcula reputación del owner del servicio
    owner_id = await recalc_user_reputation(review.service_id)
    # Recupera documento para devolverlo
    inserted = await get_review_by_id(new_id)
    return inserted

@router.get("/service/{service_id}", response_model=List[ReviewOut])
async def list_reviews_by_service(service_id: str):
    try:
        oid = ObjectId(service_id)
    except:
        raise HTTPException(400, "service_id inválido")
    return await get_reviews_by_service(oid)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: str):
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(400, "review_id inválido")
    deleted = await delete_review_by_id(oid)
    if not deleted:
        raise HTTPException(404, "Reseña no encontrada")
    return
