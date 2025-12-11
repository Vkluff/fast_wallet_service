import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your models and config
from core.config import settings
from core.models import Base

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the environment variable to indicate we're in an Alembic context
os.environ["ALEMBIC_CONTEXT"] = "true"

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata
# This will be used by 'autogenerate' to detect model changes
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations in the given connection."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata, 
        compare_type=True,
        render_as_batch=True  # For better SQLite support if needed
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Override the database URL with the one from settings
    config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
    
    # Create an async engine
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
