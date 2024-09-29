import asyncio
import sys
import logging
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from sqlalchemy.future import select
from sqlalchemy import text
from app.database import async_session, engine, Base
from app.models.models import Continent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Starting database initialization...")
    try:
        async with engine.begin() as conn:
            logger.info("Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            logger.info("Checking for existing data...")
            try:
                result = await session.execute(select(Continent))
                continents = result.scalars().all()
                if continents:
                    logger.info("Initial data already exists.")
                    return
            except ProgrammingError:
                logger.info("Tables don't exist yet. Proceeding with initialization.")
            except SQLAlchemyError as e:
                logger.error(f"Error checking for existing data: {e}")
                raise

            logger.info("Fetching and parsing SQL commands...")
            try:
                sql_commands = await fetch_and_parse_sql()
            except Exception as e:
                logger.error(f"Error fetching and parsing SQL: {e}")
                raise

            for command in sql_commands:
                sql = clean_sql_statement(command)
                if sql:
                    try:
                        logger.info(f"Executing SQL: {sql[:50]}...")  # Log first 50 chars of SQL
                        await session.execute(text(sql))
                        await session.commit()
                    except SQLAlchemyError as e:
                        logger.error(f"Error executing SQL: {e}")
                        logger.error(f"Problematic SQL: {sql}")
                        await session.rollback()

        logger.info("Database initialization completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise

if __name__ == '__main__':
    logger.info("Running database initialization script...")
    try:
        asyncio.run(init_db())
        logger.info("Script execution completed successfully.")
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)