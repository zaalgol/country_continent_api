import asyncio
import requests
import sys
import os
import re

from sqlalchemy.future import select
from sqlalchemy import text

sys.path.append(os.path.abspath('.'))
from app.database import async_session, engine, Base
from app.models.models import Continent

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(Continent))
        continents = result.scalars().all()
        if continents:
            print("Initial data already exists.")
            return

        sql_commands = await fetch_and_parse_sql()

        for command in sql_commands:
            sql = clean_sql_statement(command)
            if sql:
                try:
                    if sql.startswith("CREATE INDEX"):
                        # Execute CREATE INDEX statements separately
                        await session.execute(text(sql))
                    elif not sql.startswith("ALTER TABLE"):  # Skip ALTER TABLE statements
                        await session.execute(text(sql))
                    await session.commit()
                except Exception as e:
                    print(f"Error executing SQL: {e}")
                    print(f"Problematic SQL: {sql}")
                    await session.rollback()

        print("Continents and Countries data inserted.")

if __name__ == '__main__':
    asyncio.run(init_db())
