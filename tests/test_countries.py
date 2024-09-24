# tests/test_countries.py
import pytest
from app.schemas import CountryCreate, CountryUpdate

@pytest.mark.asyncio
async def test_create_country(client):
    # First, create the continent Asia if not already created
    continent_data = {
        "code": "AS",
        "name": "Asia"
    }
    await client.post("/continents/", json=continent_data)

    country_data = {
        "code": "JP",
        "name": "Japan",
        "full_name": "Japan",
        "iso3": "JPN",
        "number": 392,
        "continent_code": "AS"
    }
    response = await client.post("/countries/", json=country_data)
    assert response.status_code == 200
    assert response.json()["code"] == "JP"
    assert response.json()["name"] == "Japan"

@pytest.mark.asyncio
async def test_read_country(client):
    response = await client.get("/countries/JP")
    assert response.status_code == 200
    assert response.json()["code"] == "JP"
    assert response.json()["name"] == "Japan"

@pytest.mark.asyncio
async def test_update_country(client):
    update_data = {
        "name": "Japan Updated"
    }
    response = await client.put("/countries/JP", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Japan Updated"

@pytest.mark.asyncio
async def test_delete_country(client):
    response = await client.delete("/countries/JP")
    assert response.status_code == 200
    assert response.json()["detail"] == "Country deleted"

@pytest.mark.asyncio
async def test_read_nonexistent_country(client):
    response = await client.get("/countries/XX")
    assert response.status_code == 404
    assert response.json()["detail"] == "Country not found"

@pytest.mark.asyncio
async def test_search_country_by_name(client):
    # Re-create the country for searching
    country_data = {
        "code": "JP",
        "name": "Japan",
        "full_name": "Japan",
        "iso3": "JPN",
        "number": 392,
        "continent_code": "AS"
    }
    await client.post("/countries/", json=country_data)

    # Update the country name to "Japan Updated" for the search test
    update_data = {
        "name": "Japan Updated"
    }
    await client.put("/countries/JP", json=update_data)

    response = await client.get("/countries/search/Japan Updated")
    assert response.status_code == 200
    assert response.json()["name"] == "Japan Updated"
