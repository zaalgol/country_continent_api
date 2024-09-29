import asyncio
import requests
import sys
import os
import re
import logging
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.future import select
from sqlalchemy import text

sys.path.append(os.path.abspath('.'))
from app.database import async_session, engine, Base
from app.models.models import Continent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gist URL that contains the initial SQL data
GIST_URL = "https://gist.githubusercontent.com/nobuti/3816985/raw/0c3ad0cf3854bc8c4ac8dcb335ee59de5218aa4f/gistfile1.txt"

async def fetch_and_parse_sql():
    """
    Fetches the SQL file from the gist and parses the SQL commands.
    """
    response = requests.get(GIST_URL)
    if response.status_code == 200:
        sql_commands = response.text.split(";")

        return sql_commands
    else:
        raise Exception(f"Failed to fetch the SQL file. Status code: {response.status_code}")
    
def clean_sql_statement(sql):
    # Remove COMMENT clauses
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    # Remove ENGINE=InnoDB
    sql = sql.replace("ENGINE=InnoDB", "")
    # Replace ` with " for identifiers
    sql = sql.replace("`", '"')

    # Modify INSERT statement for continents
    if "INSERT INTO \"continents\"" in sql:
        sql = sql.replace("INSERT INTO \"continents\" VALUES", 
                          "INSERT INTO \"continents\" (code, name) VALUES")

    return sql.strip()

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
