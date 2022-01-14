import asyncio
from inspect import getmodule
from logging.config import fileConfig
from typing import Type

import fastapi_users_db_sqlalchemy
import sqlalchemy
import sqlalchemy_utils
from sqlalchemy import Column, engine_from_config, inspect, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from alembic.environment import MigrationContext
from core.config import settings
from db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def render_item(type_, obj: Type, autogen_context):
    """Apply custom rendering for selected items."""

    if type_ == "type":
        if (
            getmodule(obj).__package__.split(".")[0]
            == sqlalchemy_utils.__package__
        ):
            autogen_context.imports.add("import sqlalchemy_utils")
        elif (
            getmodule(obj).__package__.split(".")[0]
            == fastapi_users_db_sqlalchemy.__package__
        ):
            autogen_context.imports.add("import fastapi_users_db_sqlalchemy")

    # default rendering for other objects
    return False


def compare_type(
    migration_context: MigrationContext,
    _inspected_column: Column,  # Column in db
    metadata_column: Column,  # Column in local code
    inspected_type: Type,
    metadata_type: Type,
):
    if isinstance(metadata_type, sqlalchemy_utils.UUIDType):
        inspector: sqlalchemy.engine.Inspector = inspect(
            migration_context.bind
        )
        temp_table = metadata_column.table
        inspector.reflect_table(temp_table, None)
        return inspected_type == temp_table.columns[metadata_column.name].type
    # default comparation
    return None


def run_migrations_offline():
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
        compare_server_default=True,
        render_as_batch=True,
        render_item=render_item,
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
        render_as_batch=True,
        render_item=render_item,
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
