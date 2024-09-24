import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models' metadata
from app.models.models import Base
from app.database import DATABASE_URL

# Alembic Config object
config = context.config

# Set the SQLAlchemy URL
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Enable comparison of column types
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """
    Run migrations using the given connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Enable comparison of column types
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """
    Run migrations in 'online' mode with an async engine.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online():
    """
    Entrypoint for running migrations in 'online' mode.
    """
    asyncio.run(run_async_migrations())

# Determine if we are running in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
