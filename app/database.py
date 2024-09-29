import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Get the DATABASE_URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./countries.db")

# Heroku provides DATABASE_URL in postgres:// format, which is not compatible with SQLAlchemy
# We need to replace it with postgresql:// if it's present
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# For SQLite, we need to ensure the path is absolute
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
    if DATABASE_URL.startswith("sqlite+aiosqlite:///"):
        # It's already an absolute path
        sqlite_db_path = DATABASE_URL.split("sqlite+aiosqlite:///")[1]
    else:
        # It's a relative path, make it absolute
        sqlite_db_path = os.path.join(os.getcwd(), DATABASE_URL.split("sqlite+aiosqlite://")[1])
    DATABASE_URL = f"sqlite+aiosqlite:///{sqlite_db_path}"

print(f"Using DATABASE_URL: {DATABASE_URL}")  # Add this line for debugging

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create the async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create the base class for declarative models
Base = declarative_base()

# Dependency to get the async database session
async def get_db():
    async with async_session() as session:
        yield session