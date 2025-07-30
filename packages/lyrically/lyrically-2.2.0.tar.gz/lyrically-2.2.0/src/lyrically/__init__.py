import logging
from pathlib import Path

from .database import Database
from .utils.errors import LyricallyError
from .utils.storage import create_db_path

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Lyrically:
    """A Python client for scraping artist lyrical discographies.

    This library provides an asynchronous interface to retrieve complete
    artist discographies from AZLyrics, including album metadata and song
    lyrics, with built-in database storage and robust error handling.
    """

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        """Initialize the Lyrically instance.

        Args:
            storage_dir: Directory for database storage. Defaults to None.
        """
        db_path = create_db_path(storage_dir)
        self._db = Database(db_path)

        logger.info("Lyrically instance has been initialized.")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close()

    async def get_artist_discography(self, artist: str) -> None:
        """Scrape and store artist's complete discography in database."""
        try:
            async with self._db:
                logger.info("Setting up database.")
                await self._db._init_db()
                logger.info("Database has been setup.")

                logger.info("Starting to scrape discography for: %s", artist)

                # Implement usage here

                logger.info("Finished scraping discography for: %s", artist)
        except Exception as e:
            if isinstance(e, LyricallyError):
                raise
            raise LyricallyError(f"Failed to fetch discography for {artist}") from e

    async def _close(self) -> None:
        """Close database connection."""
        if self._db._conn:
            await self._db._disconnect()
            logger.info("Database connection closed.")
