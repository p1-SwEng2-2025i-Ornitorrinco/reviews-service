# app/crud.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

from app.models import ReviewCreate, ReviewOut

# Inicializar cliente Mongo (usa tu MONGO_URI en .env)
import os
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

# --- CRUD de Reviews ---

async def insert_review(review: ReviewCreate) -> ObjectId:
    doc = review.dict(by_alias=True)
    doc["created_at"] = datetime.utcnow()
    res = await db.reviews.insert_one(doc)
    return res.inserted_id

async def get_review_by_id(review_id: ObjectId) -> ReviewOut:
    d = await db.reviews.find_one({"_id": review_id})
    if not d:
        return None
    return ReviewOut(**d)

async def get_reviews_by_service(service_id: ObjectId) -> list[ReviewOut]:
    cursor = db.reviews.find({"service_id": service_id})
    items = []
    async for d in cursor:
        items.append(ReviewOut(**d))
    return items

async def delete_review_by_id(review_id: ObjectId) -> bool:
    res = await db.reviews.delete_one({"_id": review_id})
    return res.deleted_count == 1

# --- Reputación ---

async def recalc_user_reputation(service_id: ObjectId) -> ObjectId:
    """
    Dado un service_id:
    1) Busca el servicio para obtener owner_id.
    2) Agrega todas las reseñas de servicios de ese owner.
    3) Calcula promedio y actualiza el usuario.
    Devuelve el owner_id.
    """
    svc = await db.services.find_one({"_id": service_id})
    if not svc:
        raise ValueError("Service no encontrado")
    owner_id = svc["owner_id"]

    # Obtener IDs de todos los servicios del owner
    services = await db.services.find({"owner_id": owner_id}).to_list(length=None)
    svc_ids = [s["_id"] for s in services]

    # Agregación para promedio de rating
    pipeline = [
        {"$match": {"service_id": {"$in": svc_ids}}},
        {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
    ]
    agg = await db.reviews.aggregate(pipeline).to_list(1)
    new_rep = float(agg[0]["avgRating"]) if agg else 0.0

    # Actualizar reputación del usuario
    await db.users.update_one(
        {"_id": owner_id},
        {"$set": {"reputation": new_rep}}
    )

    return owner_id
