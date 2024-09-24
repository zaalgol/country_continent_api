from sqlite3 import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.models import Country, Continent
from typing import List, Optional
from datetime import datetime
from cachetools import TTLCache, cached


# CRUD operations for Country
async def get_country_by_name(session: AsyncSession, country_name: str) -> Optional[Country]:
    """
    Retrieve a Country by its name.
    """
    result = await session.execute(
        select(Country).where(Country.name == country_name).options(joinedload(Country.continent))
    )
    return result.scalar_one_or_none()

#  Define a cache with a max size and TTL (time-to-live)
country_cache = TTLCache(maxsize=1000, ttl=1)  # Cache up to 1000 items for 5 minutes
# @cached(cache=country_cache)
async def get_country_by_name_cached(session: AsyncSession, country_name: str) -> Optional[Country]:
    return await get_country_by_name(session, country_name)

async def get_countries(session: AsyncSession, skip: int = 0, limit: int = 10, updated_after: Optional[datetime] = None) -> List[Country]:
    """
    Retrieve a list of Countries with pagination and optional updated_at filter.
    """
    query = select(Country).offset(skip).limit(limit)
    if updated_after:
        query = query.where(Country.updated_at > updated_after)
    result = await session.execute(query)
    return result.scalars().all()

async def get_countries_after(session: AsyncSession, last_updated_at: datetime, limit: int = 10) -> List[Country]:
    result = await session.execute(
        select(Country)
        .where(Country.updated_at > last_updated_at)
        .order_by(Country.updated_at)
        .limit(limit)
    )
    return result.scalars().all()

async def create_country(session: AsyncSession, country_data) -> Country:
    """
    Create a new Country.
    """
    new_country = Country(**country_data.dict())
    session.add(new_country)
    await session.commit()
    await session.refresh(new_country)
    return new_country

async def update_country(session: AsyncSession, db_country: Country, country_data) -> Country:
    """
    Update an existing Country.
    """
    for var, value in vars(country_data).items():
        if value is not None:
            setattr(db_country, var, value)
    await session.commit()
    await session.refresh(db_country)
    return db_country

async def delete_country(session: AsyncSession, db_country: Country):
    """
    Delete a Country.
    """
    await session.delete(db_country)
    await session.commit()

# CRUD operations for Continent

async def get_continent_by_code(session: AsyncSession, code: str) -> Optional[Continent]:
    """
    Retrieve a Continent by its code.
    """
    result = await session.execute(
        select(Continent).where(Continent.code == code)
    )
    return result.scalar_one_or_none()

async def get_continents(session: AsyncSession, skip: int = 0, limit: int = 10) -> List[Continent]:
    """
    Retrieve a list of Continents with pagination.
    """
    result = await session.execute(
        select(Continent).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_continent(session: AsyncSession, continent_data) -> Continent:
    """
    Create a new Continent.
    """
    new_continent = Continent(**continent_data.dict())
    session.add(new_continent)
    await session.commit()
    await session.refresh(new_continent)
    return new_continent

async def update_continent(session: AsyncSession, db_continent: Continent, continent_data) -> Continent:
    """
    Update an existing Continent.
    """
    for var, value in vars(continent_data).items():
        if value is not None:
            setattr(db_continent, var, value)
    await session.commit()
    await session.refresh(db_continent)
    return db_continent

async def delete_continent(session: AsyncSession, db_continent: Continent):
    """
    Delete a Continent.
    """
    await session.delete(db_continent)
    await session.commit()

async def bulk_create_countries(session: AsyncSession, countries: List[Country]) -> List[Country]:
    session.add_all(countries)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    return countries

async def bulk_update_countries(session: AsyncSession, countries: List[Country]) -> List[Country]:
    for country in countries:
        session.merge(country)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    return countries
