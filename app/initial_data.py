import asyncio
import sys
import logging
import requests
import re
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from sqlalchemy.future import select
from sqlalchemy import text
from app.database import async_session, engine, Base
from app.models.models import Continent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gist URL that contains the initial SQL data
GIST_URL = "https://gist.githubusercontent.com/nobuti/3816985/raw/0c3ad0cf3854bc8c4ac8dcb335ee59de5218aa4f/gistfile1.txt"

async def fetch_and_parse_sql():
    """
    Fetches the SQL file from the gist and parses the SQL commands.
    """
    logger.info(f"Fetching SQL data from {GIST_URL}")
    response = requests.get(GIST_URL)
    if response.status_code == 200:
        sql_commands = response.text.split(";")
        logger.info(f"Successfully fetched SQL data. Found {len(sql_commands)} commands.")
        return sql_commands
    else:
        logger.error(f"Failed to fetch the SQL file. Status code: {response.status_code}")
        raise Exception(f"Failed to fetch the SQL file. Status code: {response.status_code}")

def clean_sql_statement(sql):
    # Remove COMMENT clauses
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    # Remove ENGINE=InnoDB
    sql = sql.replace("ENGINE=InnoDB", "")
    # Replace backticks with double quotes for identifiers
    sql = sql.replace("`", '"')
    # Remove UNSIGNED as it's not supported in PostgreSQL
    sql = sql.replace("UNSIGNED", "")
    # Replace INT(11) with INTEGER
    sql = re.sub(r"INT\(\d+\)", "INTEGER", sql)
    # Replace SMALLINT(x) with SMALLINT
    sql = re.sub(r"SMALLINT\(\d+\)", "SMALLINT", sql)
    # Remove ZEROFILL
    sql = sql.replace("ZEROFILL", "")
    # Replace KEY with CREATE INDEX IF NOT EXISTS
    sql = sql.replace("KEY ", "CREATE INDEX IF NOT EXISTS idx_")
    # Fix PRIMARY KEY syntax
    sql = sql.replace("PRIMARY KEY", "PRIMARY KEY ")
    # Fix FOREIGN KEY syntax
    sql = re.sub(r"CONSTRAINT\s+([^\s]+)\s+FOREIGN KEY", r"CONSTRAINT \1 FOREIGN KEY", sql)
    # Handle INSERT statements
    if sql.startswith("INSERT INTO"):
        # Replace double quotes with single quotes for string values
        sql = re.sub(r'"([^"]*)"', r"'\1'", sql)
        # Replace ( with ( and ) with ) to ensure proper formatting
        sql = sql.replace("(", "(").replace(")", ")")
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
                        if sql.startswith("CREATE INDEX") or sql.startswith("ALTER TABLE"):
                            # Execute CREATE INDEX and ALTER TABLE statements separately
                            await session.execute(text(sql))
                            await session.commit()
                        elif sql.startswith("INSERT INTO"):
                            # For INSERT statements, use parameterized queries
                            table_name = re.search(r'INSERT INTO "(\w+)"', sql).group(1)
                            columns = re.search(r'\(([^)]+)\)', sql).group(1).split(', ')
                            values = re.findall(r'\(([^)]+)\)', sql)[1:]
                            for value_set in values:
                                value_list = [v.strip().strip("'") for v in value_set.split(',')]
                                insert_stmt = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({", ".join([":"+c for c in columns])})'
                                await session.execute(text(insert_stmt), dict(zip(columns, value_list)))
                            await session.commit()
                        else:
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