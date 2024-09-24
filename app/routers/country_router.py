from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, List, Optional
from datetime import datetime

from app.database import async_session
from app.models.models import Country
from app.schemas import CountryCreate, CountryUpdate, CountryOut
from app.dependencies import get_db
from app.crud import (
    get_country_by_name_cached, get_countries, create_country, update_country, delete_country, get_countries_after
)

router = APIRouter(
    prefix="/countries",
    tags=["countries"],
    responses={404: {"description": "Not found"}},
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async database session.
    """
    async with async_session() as session:
        yield session

@router.get("/", response_model=List[CountryOut])
async def read_countries(
    skip: int = 0,
    limit: int = 10,
    updated_after: Optional[datetime] = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of countries with pagination and optional updated_at filtering.
    """
    countries = await get_countries(session, skip=skip, limit=limit, updated_after=updated_after)
    return countries

@router.get("/after", response_model=List[CountryOut])
async def read_countries_after(
    last_updated_at: datetime,
    limit: int = 10,
    session: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of countries updated after a specific timestamp with limit.
    """
    countries = await get_countries_after(session, last_updated_at, limit)
    return countries

@router.get("/{country_code}", response_model=CountryOut)
async def read_country(country_code: str, session: AsyncSession = Depends(get_db)):
    """
    Retrieve a single country by its code.
    """
    result = await session.get(Country, country_code)
    if not result:
        raise HTTPException(status_code=404, detail="Country not found")
    return result

@router.post("/", response_model=CountryOut)
async def create_new_country(country: CountryCreate, session: AsyncSession = Depends(get_db)):
    """
    Create a new country.
    """
    existing_country = await session.get(Country, country.code)
    if existing_country:
        raise HTTPException(status_code=400, detail="Country already exists")
    new_country = await create_country(session, country)
    return new_country

@router.put("/{country_code}", response_model=CountryOut)
async def update_existing_country(country_code: str, country_update: CountryUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update an existing country.
    """
    db_country = await session.get(Country, country_code)
    if not db_country:
        raise HTTPException(status_code=404, detail="Country not found")
    updated_country = await update_country(session, db_country, country_update)
    return updated_country

@router.delete("/{country_code}")
async def delete_existing_country(country_code: str, session: AsyncSession = Depends(get_db)):
    """
    Delete a country.
    """
    db_country = await session.get(Country, country_code)
    if not db_country:
        raise HTTPException(status_code=404, detail="Country not found")
    await delete_country(session, db_country)
    return {"detail": "Country deleted"}

@router.get("/search/{country_name}", response_model=CountryOut)
async def search_country_by_name(country_name: str, session: AsyncSession = Depends(get_db)):
    """
    Search for a country by name and return its details including continent.
    """
    country = await get_country_by_name_cached(session, country_name)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country
