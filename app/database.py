import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./countries.db")

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
