# Reviews Service

Microservicio para gestionar **reseñas** y **reputación** de usuarios sobre servicios.

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
   MONGO_URI=mongodb://localhost:27017/yourdb
   PORT=8000
   ```

5. Levanta el servicio:

   ```cmd
   uvicorn app.main:app --reload
   ```

6. Corre pruebas:

   ```cmd
   pytest
   ```

## 📚 Endpoints

| Método | Ruta                            | Descripción                  |
| ------ | ------------------------------- | ---------------------------- |
| GET    | `/health`                       | Estado del servicio          |
| POST   | `/reviews`                      | Crea una nueva reseña        |
| GET    | `/reviews/service/{service_id}` | Lista reseñas de un servicio |
| DELETE | `/reviews/{review_id}`          | Elimina una reseña           |

### Ejemplo de payload para POST `/reviews`

```json
{
  "service_id": "60d9f9f3e1dfe73b8c2f9abc",
  "reviewer_id": "60d9f9f3e1dfe73b8c2f9def",
  "rating": 5,
  "comment": "Excelente servicio"
}
```

## 🌳 GitFlow

* Ramas protegidas: `main`, `develop`
* Feature branches: `feature/*`
* Para iniciar:

  ```bash
  git flow init
  git checkout -b feature/reviews-module develop
  ```
* Nuevo código → PR contra `develop` → revisión → merge.

## 📈 Observabilidad

* Integrado con OpenTelemetry (FastAPI & Motor).
* Middleware para contadores de peticiones, latencias y errores.
* Se puede ver trazas/métricas con un backend compatible.

---

Con esto tienes un **servicio completo**, pruebas y documentación.
Ahora puedes crear tu PR en la rama `feature/reviews-module` para revisión.
¿Algo más en lo que te pueda ayudar?
