# app/crud.py

import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
from datetime import datetime
import os

from app.models import ReviewCreate

# Conecta a la DB correcta
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/servicios_app")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

# URL del servicio de usuarios
USUARIOS_API_URL = os.getenv("USUARIOS_API_URL", "http://localhost:8001")

async def recalc_user_reputation(service_id: ObjectId) -> str:
    """
    Recalcula la reputación del usuario dueño del servicio basado en todas las reseñas
    de todos sus servicios y actualiza la reputación en el servicio de usuarios.
    """
    # 1. Buscar el servicio en la colección ofertas
    svc = await db.ofertas.find_one({"_id": service_id})
    if not svc:
        raise ValueError("Service no encontrado")
    
    owner_id = svc.get("cliente_id")
    if not owner_id:
        raise ValueError("El servicio no tiene asignado cliente_id")

    # 2. Buscar todos los servicios del mismo usuario
    services = await db.ofertas.find({"cliente_id": owner_id}).to_list(None)
    svc_ids = [s["_id"] for s in services]
    
    # 3. Calcular promedio de ratings de todos los servicios del usuario
    pipeline = [
        {"$match": {"service_id": {"$in": svc_ids}}},
        {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
    ]
    agg = await db.reviews.aggregate(pipeline).to_list(1)
    new_rep = round(float(agg[0]["avgRating"]), 2) if agg else 0.0

    # 4. Actualizar reputación en el servicio de usuarios via HTTP
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{USUARIOS_API_URL}/users/{str(owner_id)}",
                data={"reputacion": new_rep},
                timeout=10.0
            )
            if response.status_code != 200:
                raise ValueError(f"Error al actualizar reputación en usuarios-api: {response.status_code} - {response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Error de conexión con usuarios-api: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error inesperado al actualizar reputación: {str(e)}")
    
    return str(owner_id)

# Resto de funciones sin cambios...
async def insert_review(review: ReviewCreate) -> ObjectId:
    doc = review.model_dump(by_alias=True)
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

async def get_reviews_by_reviewer(reviewer_id: ObjectId) -> List[dict]:
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
    return out