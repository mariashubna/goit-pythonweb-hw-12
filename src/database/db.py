"""Database session management module.

This module provides database connection and session management functionality using SQLAlchemy's
async features. It includes a session manager class that handles connection pooling,
session creation, and automatic cleanup of database resources.

The module uses environment variables for database configuration (see config.py).
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """Manages database sessions and connections.

    This class provides a context manager for handling database sessions,
    ensuring proper resource cleanup and transaction management.

    Attributes:
        _engine (AsyncEngine | None): SQLAlchemy async engine instance.
        _session_maker (async_sessionmaker): Factory for creating new database sessions.
    """

    def __init__(self, url: str):
        """Initialize the database session manager.

        Args:
            url (str): Database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """Create and manage a database session.

        This async context manager creates a new database session and handles:
        - Automatic rollback on errors
        - Session cleanup after use
        - Exception propagation

        Yields:
            AsyncSession: An active database session.

        Raises:
            Exception: If database session is not initialized
            SQLAlchemyError: If a database error occurs
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


# Global session manager instance
sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """FastAPI dependency for database session management.

    This async generator function provides a database session for FastAPI
    route handlers. It automatically manages the session lifecycle.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use the database session
            pass

    Yields:
        AsyncSession: A database session for use in route handlers.
    """
    async with sessionmanager.session() as session:
        yield session
