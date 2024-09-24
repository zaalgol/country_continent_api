from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, List

from app.database import async_session
from app.models.models import Continent
from app.schemas import ContinentCreate, ContinentUpdate, ContinentOut
from app.dependencies import get_db
from app.crud import (
    get_continent_by_code, get_continents, create_continent, update_continent, delete_continent
)

router = APIRouter(
    prefix="/continents",
    tags=["continents"],
    responses={404: {"description": "Not found"}},
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async database session.
    """
    async with async_session() as session:
        yield session

@router.get("/", response_model=List[ContinentOut])
async def read_continents(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of continents with pagination.
    """
    continents = await get_continents(session, skip=skip, limit=limit)
    return continents

@router.get("/{continent_code}", response_model=ContinentOut)
async def read_continent(continent_code: str, session: AsyncSession = Depends(get_db)):
    """
    Retrieve a single continent by its code.
    """
    continent = await get_continent_by_code(session, continent_code)
    if not continent:
        raise HTTPException(status_code=404, detail="Continent not found")
    return continent

@router.post("/", response_model=ContinentOut)
async def create_new_continent(continent: ContinentCreate, session: AsyncSession = Depends(get_db)):
    """
    Create a new continent.
    """
    existing_continent = await get_continent_by_code(session, continent.code)
    if existing_continent:
        raise HTTPException(status_code=400, detail="Continent already exists")
    new_continent = await create_continent(session, continent)
    return new_continent

@router.put("/{continent_code}", response_model=ContinentOut)
async def update_existing_continent(continent_code: str, continent_update: ContinentUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update an existing continent.
    """
    db_continent = await get_continent_by_code(session, continent_code)
    if not db_continent:
        raise HTTPException(status_code=404, detail="Continent not found")
    updated_continent = await update_continent(session, db_continent, continent_update)
    return updated_continent

@router.delete("/{continent_code}")
async def delete_existing_continent(continent_code: str, session: AsyncSession = Depends(get_db)):
    """
    Delete a continent.
    """
    db_continent = await get_continent_by_code(session, continent_code)
    if not db_continent:
        raise HTTPException(status_code=404, detail="Continent not found")
    await delete_continent(session, db_continent)
    return {"detail": "Continent deleted"}