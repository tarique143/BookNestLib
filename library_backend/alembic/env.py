# Postgres sql 
# file: alembic/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- NAYA AUR ZAROORI CODE ---
# Isse Alembic ko project ka root folder milta hai, taaki woh 'models' 
# aur 'database' folders se files import kar sake.
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# .env se config load karne ke liye
from dotenv import load_dotenv
load_dotenv()

# Apne project ke Base object ko import karein jo sabhi models ka parent hai.
from database import Base

# Apne sabhi models ko yahan import karein. Yeh bahut zaroori hai.
from models.user_model import User, Role
from models.book_model import Book, Category, Subcategory
from models.language_model import Language
from models.library_management_models import Location, BookCopy, IssuedBook, DigitalAccess
from models.permission_model import Permission
from models.request_model import UploadRequest
from models.log_model import Log
from models.book_permission_model import BookPermission
# --- NAYA CODE YAHAN KHATM ---


# Alembic config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogeneration
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("DATABASE_URL not found in environment.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")  # --- BADLAV YAHAN ---

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# Migration mode check
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
