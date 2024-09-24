from typing import AsyncGenerator
from app.database import AsyncSession
from app.database import async_session

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
