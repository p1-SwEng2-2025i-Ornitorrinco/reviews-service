# Reviews Service

Microservicio para gestionar **reseñas** y **reputación** de usuarios sobre servicios.

---

## 🚀 Levantar localmente

1. Clona el repositorio y entra en él:
   ```bash
   git clone git@github.com:p1-SwEng2-2025i-Ornitorrinco/reviews-service.git
   cd reviews-service


2. Crea y activa el entorno virtual (Windows + CMD):

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instala dependencias:

   ```cmd
   pip install -r requirements.txt
   ```

4. Configura variables de entorno en un archivo `.env`:

   ```dotenv
   MONGO_URI=mongodb://localhost:27017/servicios_app
   PORT=8003
   USUARIOS_API_URL=http://localhost:8000
   ```

5. Levanta el servicio:

   ```cmd
   uvicorn app.main:app --reload
   ```

6. (Opcional) Arrancar con Docker Compose:

   ```bash
   docker-compose up --build
   ```

7. Corre pruebas y genera reporte de cobertura:

   ```bash
   pytest --cov=app
   ```

---

## 📚 Endpoints

| Método | Ruta                              | Descripción                                                      |
| ------ | --------------------------------- | ---------------------------------------------------------------- |
| GET    | `/health`                         | Estado del servicio                                              |
| GET    | `/metrics`                        | Métricas Prometheus (peticiones, latencias, errores, tamaños)    |
| POST   | `/reviews`                        | Crea una nueva reseña; recalcula reputación y actualiza usuarios |
| GET    | `/reviews/service/{service_id}`   | Lista reseñas de un servicio                                     |
| GET    | `/reviews/reviewer/{reviewer_id}` | Lista reseñas hechas por un reviewer                             |
| DELETE | `/reviews/{review_id}`            | Elimina una reseña                                               |

### Swagger / OpenAPI

Accede a la UI interactiva en:

```
http://localhost:8003/docs
```
---

