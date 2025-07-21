# Changelog

Todas las modificaciones relevantes realizadas al microservicio **reviews-service**.

## \[Unreleased]

### Changed

* Mejoras en observabilidad: integración de métricas HTTP (peticiones activas, latencia, tamaños de respuesta) y expositor Prometheus en `/metrics`.
* Ajuste de middleware para capturar contadores de peticiones, histogramas de latencia y recuento de errores por endpoint.
* Corrección en `recalc_user_reputation`: manejo de timeouts y errores en la llamada a usuarios-api al actualizar reputación.
* Refactor de actualización de reputación: redondeo a dos decimales y mensajes de error detallados ante fallos de conexión.

### Added

* Endpoint `/reviews/reviewer/{reviewer_id}` para listar reseñas por usuario.
* Unificación de rutas de publicaciones y reseñas bajo `/reviews`.

### Added

* Instrumentación completa con OpenTelemetry:

  * Contador de peticiones HTTP.
  * Histogramas de latencia (ms) y tamaño de respuesta (bytes).
  * Métricas de errores por endpoint.
* Endpoint `/metrics` para exponer métricas Prometheus.
* Integración con servicio de usuarios para enriquecimiento de datos en publicaciones (foto y reputación).
* Nuevo endpoint **GET** `/reviews/reviewer/{reviewer_id}` para listar reseñas por reviewer.

### Changed

* Unificación de rutas, eliminando prefijo `/publicaciones` y consolidando todo bajo `/reviews`:

  * **GET** `/reviews/{user_id}` → obtenión de publicaciones (ofertas) de un usuario cliente.
* Refactor de `app/routers/reviews.py` y `app/main.py` para incluir solo el router `reviews`.
* Variables de entorno renombradas y unificadas (`USUARIOS_API_URL`).
* Reestructuración de `app/crud.py`:

  * Separación de funciones CRUD y de recálculo de reputación.
  * Manejo robusto de errores de conexión y tiempo de espera al llamar a usuarios-api.
  * Cálculo de reputación promedio redondeado a 2 decimales.
* Configuración de CORS en FastAPI (permitir front) en `main.py`.
* Migración a Pydantic V2: actualización de `schema_extra` a `json_schema_extra` en ejemplos.

### Fixed

* Serialización de `ObjectId` en respuestas:

  * Conversión a `str(...)` en `get_review_by_id`, `get_reviews_by_service` y `get_reviews_by_reviewer`.
* Corrección de importaciones y eliminación de routers duplicados (`pub_router`).
* Corrección de errores de routing en Swagger:

  * Eliminado el parámetro erróneo `router.app.mongodb` y uso directo de `db` importado.
* Manejo de errores HTTP y status codes adecuados (`resp.raise_for_status()`, `HTTPException`).

## \[0.1.0] - 2025-07-21

### Initial release

* Creación del microservicio base con FastAPI y Motor:

  * Endpoints CRUD para reseñas (`POST`, `GET /service/{}`, `DELETE`).
  * Conexión a MongoDB.
  * Plantilla de observabilidad inicial sin métricas.

---
