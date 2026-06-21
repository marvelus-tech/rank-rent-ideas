"""Async database engine/session management and migration helpers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from mirror_sniper.config import Settings, load_settings

from .models import Base


class DatabaseManager:
    """Owns async SQLAlchemy engine and session factory lifecycle."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.engine: AsyncEngine = create_async_engine(
            self.settings.app.database.url,
            echo=self.settings.app.database.echo,
            future=True,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Yield a managed async session with automatic rollback on error."""

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def init_db(self) -> None:
        """Create all database tables if they do not exist."""

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """Dispose the database engine and release pooled connections."""

        await self.engine.dispose()


def run_migrations(alembic_ini_path: str | Path = "mirror_sniper/alembic.ini") -> None:
    """Run Alembic migrations to head if Alembic is configured.

    Raises:
        FileNotFoundError: If alembic.ini is missing.
    """

    ini = Path(alembic_ini_path)
    if not ini.exists():
        raise FileNotFoundError(
            f"Alembic config not found at {ini}. Initialize Alembic before running migrations."
        )

    config = Config(str(ini))
    command.upgrade(config, "head")


async def initialize_database(settings: Settings | None = None, run_alembic: bool = False) -> DatabaseManager:
    """Initialize DB manager and create schema (and optionally run Alembic)."""

    manager = DatabaseManager(settings=settings)
    if run_alembic:
        run_migrations()
    else:
        await manager.init_db()
    return manager
