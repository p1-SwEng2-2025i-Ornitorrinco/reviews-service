# app/crud.py

import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
from datetime import datetime
import os
import logging

from app.models import ReviewCreate
from app.clients.users_client import users_client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conecta a la DB correcta
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/servicios_app")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

async def insert_review(review: ReviewCreate) -> ObjectId:
    # review.model_dump(by_alias=True) usa los aliases de Pydantic
    doc = review.model_dump(by_alias=True)
    # Asegurarnos de que Mongo almacene ObjectId, no strings:
    from bson import ObjectId as _OID
    doc["service_id"]  = _OID(doc["service_id"])
    doc["reviewer_id"] = _OID(doc["reviewer_id"])
    doc["created_at"] = datetime.utcnow()
    res = await db.reviews.insert_one(doc)
    return res.inserted_id

async def get_review_by_id(review_id: ObjectId) -> dict:
    d = await db.reviews.find_one({"_id": review_id})
    if not d:
        return None
    # convierte todos los campos a tipos primitivos
    return {
        "id":          str(d["_id"]),
        "service_id":  str(d["service_id"]),
        "reviewer_id": str(d["reviewer_id"]),
        "rating":      d["rating"],
        "comment":     d.get("comment"),
        "created_at":  d["created_at"].isoformat(),
    }

async def get_reviews_by_service(service_id: ObjectId) -> list[dict]:
    cursor = db.reviews.find({"service_id": service_id})
    out = []
    async for d in cursor:
        out.append({
            "id":          str(d["_id"]),
            "service_id":  str(d["service_id"]),
            "reviewer_id": str(d["reviewer_id"]),
            "rating":      d["rating"],
            "comment":     d.get("comment"),
            "created_at":  d["created_at"].isoformat(),
        })
    return out

async def delete_review_by_id(review_id: ObjectId) -> bool:
    res = await db.reviews.delete_one({"_id": review_id})
    return res.deleted_count == 1

async def recalc_user_reputation(service_id: ObjectId) -> str:
    svc = await db.ofertas.find_one({"_id": service_id})
    if not svc:
        raise ValueError("Service no encontrado")
    owner_id = svc.get("cliente_id")
    if not owner_id:
        raise ValueError("El servicio no tiene asignado cliente_id")

    # Recalcula promedio
    services = await db.ofertas.find({"cliente_id": owner_id}).to_list(None)
    svc_ids = [s["_id"] for s in services]
    pipeline = [
        {"$match": {"service_id": {"$in": svc_ids}}},
        {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
    ]
    agg = await db.reviews.aggregate(pipeline).to_list(1)
    new_rep = float(agg[0]["avgRating"]) if agg else 0.0

    # Actualiza reputación
    await db.users.update_one(
        {"_id": owner_id},
        {"$set": {"reputation": new_rep}}
    )
    return str(owner_id)


async def recalc_user_reputation(service_id: ObjectId) -> str:
    """
    Recalcula la reputación del propietario de un servicio y la actualiza
    en el servicio de usuarios mediante HTTP.
    """
    try:
        # Buscar el servicio en la base de datos local
        svc = await db.ofertas.find_one({"_id": service_id})
        if not svc:
            logger.error(f"Servicio {service_id} no encontrado")
            raise ValueError("Service no encontrado")
        
        owner_id = svc.get("cliente_id")
        if not owner_id:
            logger.error(f"Servicio {service_id} no tiene cliente_id asignado")
            raise ValueError("El servicio no tiene asignado cliente_id")

        # Verificar que el usuario existe en el otro servicio
        user_info = await users_client.get_user_by_id(str(owner_id))
        if not user_info:
            logger.error(f"Usuario {owner_id} no encontrado en el servicio de usuarios")
            raise ValueError(f"Usuario {owner_id} no encontrado en el servicio de usuarios")

        # Obtener todos los servicios del usuario
        services = await db.ofertas.find({"cliente_id": owner_id}).to_list(None)
        svc_ids = [s["_id"] for s in services]
        
        # Calcular promedio de ratings
        pipeline = [
            {"$match": {"service_id": {"$in": svc_ids}}},
            {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
        ]
        agg = await db.reviews.aggregate(pipeline).to_list(1)
        new_reputation = float(agg[0]["avgRating"]) if agg else 0.0
        
        # Actualizar reputación en el servicio de usuarios
        success = await users_client.update_user_reputation(str(owner_id), new_reputation)
        
        if not success:
            logger.error(f"No se pudo actualizar la reputación del usuario {owner_id}")
            raise ValueError(f"No se pudo actualizar la reputación del usuario {owner_id}")
        
        logger.info(f"Reputación actualizada exitosamente para usuario {owner_id}: {new_reputation}")
        return str(owner_id)
        
    except Exception as e:
        logger.error(f"Error en recalc_user_reputation: {str(e)}")
        raise

async def get_reviews_by_reviewer(reviewer_id: ObjectId) -> List[dict]:
    """
    Devuelve una lista de dicts (con campos serializables) de todas las reseñas
    cuyo reviewer_id coincide.
    """
    cursor = db.reviews.find({"reviewer_id": reviewer_id})
    out = []
    async for d in cursor:
        out.append({
            "id":          str(d["_id"]),
            "service_id":  str(d["service_id"]),
            "reviewer_id": str(d["reviewer_id"]),
            "rating":      d["rating"],
            "comment":     d.get("comment"),
            "created_at":  d["created_at"].isoformat(),
        })
