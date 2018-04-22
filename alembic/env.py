from logging.config import fileConfig
import sys
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

BASE_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_PATH)

from socialcrawler.utils import get_config
from socialcrawler.models import Base


package_config = get_config()
alembic_config = context.config
fileConfig(alembic_config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    context.configure(url=package_config.db.url, target_metadata=target_metadata, literal_binds=True, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        url=package_config.db.url
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
