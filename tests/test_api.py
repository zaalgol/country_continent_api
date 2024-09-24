import sys
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


sys.path.append(os.path.abspath('.'))
from app.main import app
from app.database import Base, engine

# Create a new AsyncSession for testing
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

