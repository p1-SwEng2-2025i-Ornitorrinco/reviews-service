# tests/test_reviews.py
import pytest
from httpx import AsyncClient
from app.main import app
from bson import ObjectId

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.anyio
async def test_create_and_list_and_delete_review(client):
    # Crear ids falsos
    service_id  = str(ObjectId())
    reviewer_id = str(ObjectId())

    # POST /reviews
    payload = {
        "service_id": service_id,
        "reviewer_id": reviewer_id,
        "rating": 4,
        "comment": "Muy buen servicio"
    }
    r1 = await client.post("/reviews", json=payload)
    assert r1.status_code == 201
    data = r1.json()
    assert data["rating"] == 4
    rev_id = data["id"]

    # GET /reviews/service/{service_id}
    r2 = await client.get(f"/reviews/service/{service_id}")
    assert r2.status_code == 200
    arr = r2.json()
    assert any(item["id"] == rev_id for item in arr)

    # DELETE /reviews/{review_id}
    r3 = await client.delete(f"/reviews/{rev_id}")
    assert r3.status_code == 204
