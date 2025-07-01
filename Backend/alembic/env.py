from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the Base from your application's database core.
# This Base object should have all your SQLAlchemy models registered with it.
from app.core.database import Base

# To ensure Alembic's autogenerate feature can detect all model changes,
# import all your model modules here. This registers them with Base.metadata.
# If your models are structured within a package (e.g., app.models) and
# app.models.__init__.py imports all individual model files, then
# importing just app.models might be sufficient.
# However, explicit imports are safer for clarity.
import app.models.user          # Contains User model
import app.models.account       # Contains Account model
import app.models.document      # Contains Document model
import app.models.document_info # Contains DocumentInfo model
# Add any other model files from your application here, e.g.:
# import app.models.admin_specific_tables

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata should point to your SQLAlchemy models' MetaData object.
# This is used by Alembic's 'autogenerate' feature to compare the database
# schema against your models and generate migration scripts.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
