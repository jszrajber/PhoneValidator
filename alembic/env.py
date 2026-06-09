from logging.config import fileConfig
import logging
import os
import sys

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Ensure the repository root is on sys.path so backend packages are importable
# ---------------------------------------------------------------------------
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")

# ---------------------------------------------------------------------------
# Import project settings and SQLAlchemy metadata
# ---------------------------------------------------------------------------
from backend.core.config import settings   # noqa: E402
from backend.db.base import Base           # noqa: E402
from backend.models.check import NumberCheck

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Build a *synchronous* SQLAlchemy URL from the async DATABASE_URL.
# asyncpg cannot be used by Alembic directly, so we strip the "+asyncpg" part.
# ---------------------------------------------------------------------------
sync_url = (
    settings.DATABASE_URL
    .replace("+asyncpg", "")
    .replace(f"@{settings.POSTGRES_SERVER}:", "@localhost:")
)
config.set_main_option("sqlalchemy.url", sync_url)
logger.info("Alembic using sqlalchemy.url: %s", sync_url)


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL output)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()