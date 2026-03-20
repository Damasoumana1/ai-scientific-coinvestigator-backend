from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import de la configuration de l'application
import sys
import os

# Ajout du répertoire racine au path pour importer app.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.settings import settings
from app.db.base import Base

# Import de tous les modèles pour les inclure dans les migrations
from app.db.models import (  # noqa: F401
    user,
    project,
    research_paper,
    paper_chunk,
    analysis_run,
    contradiction,
    research_gap,
    protocol,
    reasoning_trace,
    export,
    activity_log,
)

# Alembic Config object (accès à .ini)
config = context.config

# Surcharge dynamique de l'URL DB depuis les settings (.env)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Setup logging depuis le fichier .ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Les métadonnées pour l'autogénération des migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Migrations en mode 'offline' (sans connexion DB active)."""
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


def run_migrations_online() -> None:
    """Migrations en mode 'online' (avec connexion DB active)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
