import logging
from pathlib import Path

import aiosqlite

from ..utils.errors import LyricallyConnectionError, LyricallyDataError

logger = logging.getLogger(__name__)


class Database:
    """Handle database operations."""

    def __init__(self, db_path: Path) -> None:
        """Initialize the Database instance.

        Args:
            db_path: The desired path for database storage.
        """
        self._db_path = db_path
        self._is_setup = False
        self._conn: aiosqlite.Connection | None = None

        logger.debug("Database instance has been initialized.")

    async def __aenter__(self):
        """Async context manager entry."""
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._disconnect()

    async def _connect(self) -> None:
        """Establish database connection."""
        if self._conn is None:
            try:
                self._conn = await aiosqlite.connect(self._db_path, timeout=10.0)

                # Add performance optimizations and foreign key support
                await self._conn.execute("PRAGMA foreign_keys = ON;")
                await self._conn.execute("PRAGMA synchronous = NORMAL;")
                await self._conn.execute("PRAGMA cache_size = 1000;")
                await self._conn.execute("PRAGMA temp_store = MEMORY;")

                logger.debug("Database connection established.")
            except aiosqlite.Error as e:
                raise LyricallyConnectionError("Failed to connect to database") from e

    async def _disconnect(self) -> None:
        """Close database connection."""
        if self._conn:
            try:
                await self._conn.close()
                self._conn = None
                logger.debug("Database connection closed.")
            except aiosqlite.Error as e:
                self._conn = None
                raise LyricallyConnectionError(
                    "Error occurred while closing database connection"
                ) from e

    async def _init_db(self) -> None:
        """Initialize database schema if not already set up."""
        if not self._is_setup:
            try:
                await self._connect()

                # Artists table
                await self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS artists (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        url TEXT UNIQUE NOT NULL
                    )
                    """
                )

                # Albums table
                await self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS albums (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        artist_id INTEGER NOT NULL,
                        FOREIGN KEY (artist_id) REFERENCES artists (id)
                            ON DELETE CASCADE,
                        UNIQUE (artist_id, title)
                    )
                    """
                )

                # Tracks table
                await self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tracks (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        lyrics TEXT,
                        album_id INTEGER NOT NULL,
                        FOREIGN KEY (album_id) REFERENCES albums (id)
                            ON DELETE CASCADE,
                        UNIQUE (album_id, title)
                    )
                    """
                )

                await self._conn.commit()
                logger.debug("Database schema initialized")
                self._is_setup = True

            except aiosqlite.Error as e:
                raise LyricallyDataError(
                    "Error occurred while attempting to initialize database schema."
                ) from e
