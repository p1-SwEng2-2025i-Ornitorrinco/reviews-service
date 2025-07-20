# app/routers/reviews.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId

from app.models import ReviewCreate, ReviewOut
from app.crud import (
    insert_review,
    get_review_by_id,
    get_reviews_by_service,
    delete_review_by_id,
    recalc_user_reputation,
    get_reviews_by_reviewer,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate):
    new_id = await insert_review(review)
    try:
        await recalc_user_reputation(ObjectId(review.service_id))
    except ValueError as e:
        await delete_review_by_id(new_id)
        raise HTTPException(404, detail=str(e))
    dto = await get_review_by_id(new_id)
    if not dto:
        raise HTTPException(500, "Error interno al leer la reseña creada")
    return dto

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
    if not await delete_review_by_id(oid):
        raise HTTPException(404, "Reseña no encontrada")
    return


@router.get("/reviewer/{reviewer_id}", response_model=List[ReviewOut])
async def list_reviews_by_reviewer(reviewer_id: str):
    try:
        oid = ObjectId(reviewer_id)
    except:
        raise HTTPException(status_code=400, detail="reviewer_id inválido")
    reviews = await get_reviews_by_reviewer(oid)
    return reviews