# app/clients/users_client.py
import httpx
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UsersClient:
    def __init__(self):
        self.base_url = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")
        self.timeout = 30.0
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica de un usuario por su ID
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_id}")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al obtener usuario {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener usuario {user_id}: {e}")
            return None
    
    async def update_user_reputation(self, user_id: str, reputation: float) -> bool:
        """
        Actualiza la reputación de un usuario específico
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Preparar datos para el formulario
                data = {
                    "reputacion": reputation
                }
                
                response = await client.put(
                    f"{self.base_url}/users/{user_id}",
                    data=data
                )
                
                if response.status_code == 404:
                    logger.warning(f"Usuario {user_id} no encontrado para actualizar reputación")
                    return False
                
                response.raise_for_status()
                logger.info(f"Reputación actualizada para usuario {user_id}: {reputation}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al actualizar reputación del usuario {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al actualizar reputación del usuario {user_id}: {e}")
            return False
    
    async def get_user_basic_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica del usuario (nombre y foto)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_id}/nombre_foto")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al obtener info básica del usuario {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener info básica del usuario {user_id}: {e}")
            return None

# Instancia global del cliente
users_client = UsersClient()