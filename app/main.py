# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.observability import init_observability
from app.routers.reviews import router as reviews_router


# 1) Cargar variables de entorno
load_dotenv()

def _mongo_uri() -> str:
    # Prioriza variables de despliegue (Heroku suele usar MONGODB_URI)
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    if uri:
        return uri
    # Fallback para desarrollo local
    return "mongodb://localhost:27017/servicios_app"

MONGO_URI = _mongo_uri()
PORT      = int(os.getenv("PORT", 8000))

# 2) Crear instancia FastAPI
app = FastAPI(title="Reviews Service")

# Permitir peticiones desde frontends (Skilltrade web/móvil) y pruebas locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Conectar Mongo
mongo_client = AsyncIOMotorClient(MONGO_URI)
app.mongodb = mongo_client.get_default_database()

# 4) Inicializar observabilidad
init_observability(app, mongo_client)

# 5) Incluir routers
app.include_router(reviews_router)

# 6) Endpoint healthcheck (útil para pruebas)
@app.get("/health")
async def health():
    return {"status": "ok"}

# 7) Arrancar servidor
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
