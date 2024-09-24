# tests/test_continents.py
import pytest
from app.schemas import ContinentCreate, ContinentUpdate

@pytest.mark.asyncio
async def test_create_continent(client):
    continent_data = {
        "code": "AS",
        "name": "Asia"
    }
    response = await client.post("/continents/", json=continent_data)
    assert response.status_code == 200
    assert response.json()["code"] == "AS"
    assert response.json()["name"] == "Asia"

@pytest.mark.asyncio
async def test_read_continent(client):
    response = await client.get("/continents/AS")
    assert response.status_code == 200
    assert response.json()["code"] == "AS"
    assert response.json()["name"] == "Asia"

@pytest.mark.asyncio
async def test_update_continent(client):
    update_data = {
        "name": "Asia Updated"
    }
    response = await client.put("/continents/AS", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Asia Updated"

@pytest.mark.asyncio
async def test_delete_continent(client):
    response = await client.delete("/continents/AS")
    assert response.status_code == 200
    assert response.json()["detail"] == "Continent deleted"

@pytest.mark.asyncio
async def test_read_nonexistent_continent(client):
    response = await client.get("/continents/XX")
    assert response.status_code == 404
    assert response.json()["detail"] == "Continent not found"
