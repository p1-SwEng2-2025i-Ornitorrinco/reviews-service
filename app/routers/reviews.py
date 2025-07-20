# app/routers/reviews.py (ACTUALIZADO)
from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
import logging

from app.models import ReviewCreate, ReviewOut, ReviewWithUserInfo
from app.crud import (
    insert_review,
    get_review_by_id,
    get_reviews_by_service,
    delete_review_by_id,
    recalc_user_reputation,
    get_reviews_by_reviewer,
    get_reviews_with_user_info,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate):
    """
    Crea una nueva review y actualiza la reputación del propietario del servicio
    """
    new_id = await insert_review(review)
    
    try:
        # Actualizar reputación del propietario del servicio
        owner_id = await recalc_user_reputation(ObjectId(review.service_id))
        logger.info(f"Reputación recalculada para usuario {owner_id} tras nueva review")
    except ValueError as e:
        # Si falla la actualización de reputación, eliminar la review creada
        await delete_review_by_id(new_id)
        logger.error(f"Error al recalcular reputación: {e}")
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        # Si hay un error inesperado, también eliminar la review
        await delete_review_by_id(new_id)
        logger.error(f"Error inesperado al recalcular reputación: {e}")
        raise HTTPException(500, detail="Error interno al procesar la review")
    
    # Obtener y retornar la review creada
    dto = await get_review_by_id(new_id)
    if not dto:
        raise HTTPException(500, "Error interno al leer la reseña creada")
    return dto

@router.get("/service/{service_id}", response_model=List[ReviewOut])
async def list_reviews_by_service(service_id: str):
    """
    Lista todas las reviews de un servicio específico
    """
    try:
        oid = ObjectId(service_id)
    except:
        raise HTTPException(400, "service_id inválido")
    return await get_reviews_by_service(oid)

@router.get("/service/{service_id}/with-user-info", response_model=List[ReviewWithUserInfo])
async def list_reviews_with_user_info(service_id: str):
    """
    Lista todas las reviews de un servicio incluyendo información del reviewer
    """
    try:
        oid = ObjectId(service_id)
    except:
        raise HTTPException(400, "service_id inválido")
    
    return await get_reviews_with_user_info(oid)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: str):
    """
    Elimina una review específica
    """
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(400, "review_id inválido")
    
    if not await delete_review_by_id(oid):
        raise HTTPException(404, "Reseña no encontrada")
    
    # TODO: Opcionalmente, recalcular reputación después de eliminar
    # Sería necesario obtener el service_id de la review antes de eliminarla
    
    return

@router.get("/reviewer/{reviewer_id}", response_model=List[ReviewOut])
async def list_reviews_by_reviewer(reviewer_id: str):
    """
    Lista todas las reviews realizadas por un usuario específico
    """
    try:
        oid = ObjectId(reviewer_id)
    except:
        raise HTTPException(status_code=400, detail="reviewer_id inválido")
    
    reviews = await get_reviews_by_reviewer(oid)
    return reviews

@router.get("/service/{service_id}/stats")
async def get_service_review_stats(service_id: str):
    """
    Obtiene estadísticas de las reviews de un servicio
    """
    try:
        oid = ObjectId(service_id)
    except:
        raise HTTPException(400, "service_id inválido")
    
    reviews = await get_reviews_by_service(oid)
    
    if not reviews:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    ratings = [review["rating"] for review in reviews]
    average_rating = sum(ratings) / len(ratings)
    
    rating_distribution = {i: ratings.count(i) for i in range(1, 6)}
    
    return {
        "total_reviews": len(reviews),
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_distribution
    }