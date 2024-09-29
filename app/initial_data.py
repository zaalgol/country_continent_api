import asyncio
import sys
import logging
import requests
import re
import shlex
from sqlalchemy.exc import SQLAlchemyError
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
    # Replace SMALLINT(3) ZEROFILL with INTEGER
    sql = re.sub(r"SMALLINT\(\d+\)\s+ZEROFILL", "INTEGER", sql)
    # Replace KEY with CREATE INDEX IF NOT EXISTS
    sql = sql.replace("KEY ", "CREATE INDEX IF NOT EXISTS idx_")
    # Fix PRIMARY KEY syntax
    sql = sql.replace("PRIMARY KEY", "PRIMARY KEY ")
    # Fix FOREIGN KEY syntax
    sql = re.sub(r"CONSTRAINT\s+([^\s]+)\s+FOREIGN KEY", r"CONSTRAINT \1 FOREIGN KEY", sql)
    
    return sql.strip()

def parse_value_set(value_set):
    """
    Parses a value set string into individual values, correctly handling commas within quoted strings.
    """
    # Remove surrounding parentheses
    value_set = value_set.strip('()')
    lexer = shlex.shlex(value_set, posix=True)
    lexer.whitespace_split = True
    lexer.whitespace = ','
    lexer.quotes = '"\''
    lexer.escape = ''
    values = list(lexer)
    # Remove surrounding quotes and strip whitespace
    values = [v.strip('"\'').strip() for v in values]
    return values

async def drop_and_create_tables():
    """
    Drops all tables and recreates them based on the SQLAlchemy models.
    """
    async with engine.begin() as conn:
        logger.info("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

async def process_sql_commands(sql_commands):
    """
    Processes a list of SQL commands.
    """
    async with async_session() as session:
        for i, command in enumerate(sql_commands):
            sql = clean_sql_statement(command)
            if sql:
                logger.info(f"Processing SQL command {i+1}/{len(sql_commands)}")
                logger.info(f"Cleaned SQL: {sql[:100]}...")  # Log first 100 characters
                await process_sql_command(sql, session)

async def process_sql_command(sql, session): 
    """
    Processes a single SQL command.
    """
    try:
        if sql.startswith("CREATE TABLE"):
            logger.info("Skipping CREATE TABLE statement (already handled by SQLAlchemy)")
        elif sql.startswith("CREATE INDEX"):
            logger.info("Skipping CREATE INDEX statement (already handled by SQLAlchemy)")
        elif sql.startswith('INSERT INTO "continents"'):
            await insert_into_continents(sql, session)
        elif sql.startswith('INSERT INTO "countries"'):
            await insert_into_countries(sql, session)
        else:
            logger.info("Skipping unknown SQL statement")
        logger.info("SQL command executed successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error executing SQL: {e}")
        logger.error(f"Problematic SQL: {sql}")
        await session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Problematic SQL: {sql}")
        await session.rollback()
        raise

async def insert_into_continents(sql, session):
    """
    Processes and executes INSERT INTO continents statements.
    """
    logger.info("Executing INSERT INTO continents statement")
    values_list = re.findall(r'\(([^)]+)\)', sql)
    for value_set in values_list:
        values = parse_value_set(value_set)
        logger.info(f"Parsed values for continents: {values}")
        await session.execute(
            text("INSERT INTO continents (code, name) VALUES (:code, :name)"),
            {"code": values[0], "name": values[1]}
        )
    await session.commit()
    logger.info(f"Inserted {len(values_list)} rows into continents")

async def insert_into_countries(sql, session):
    """
    Processes and executes INSERT INTO countries statements.
    """
    logger.info("Executing INSERT INTO countries statement")
    match = re.search(r'INSERT INTO "countries"\s*\(([^)]+)\)\s*VALUES\s*(.*)', sql, re.DOTALL)
    if match:
        columns_str = match.group(1)
        values_str = match.group(2)
        columns = [col.strip().strip('"') for col in columns_str.split(',')]
        logger.info(f"Columns: {columns}")

        # Extract each value set from the VALUES part
        values_list = re.findall(r'\((.*?)\)(?:,|$)', values_str, re.DOTALL)
        for value_set in values_list:
            values = parse_value_set(value_set)
            logger.info(f"Values: {values}")

            params = dict(zip(columns, values))
            logger.info(f"Params before conversion: {params}")

            # Convert 'number' field to integer
            if 'number' in params:
                logger.info(f"Raw 'number' value before conversion: {params['number']}")
                try:
                    params['number'] = int(params['number'].lstrip('0') or '0')
                    logger.info(f"'number' value converted to integer: {params['number']}")
                except ValueError:
                    logger.error(f"Invalid 'number' value: {params['number']}")
                    raise ValueError(f"Invalid 'number' value: {params['number']}")

            logger.info(f"Params after conversion: {params}")
            await session.execute(
                text(f"INSERT INTO countries ({', '.join(columns)}) VALUES ({', '.join([':'+col for col in columns])})"),
                params
            )
        await session.commit()
        logger.info(f"Inserted {len(values_list)} rows into countries")
    else:
        logger.error("Failed to parse INSERT INTO countries statement")

async def init_db():
    logger.info("Starting database initialization...")
    try:
        await drop_and_create_tables()
        sql_commands = await fetch_and_parse_sql()
        await process_sql_commands(sql_commands)
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
