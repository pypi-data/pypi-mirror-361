import logging
from pathlib import Path

import platformdirs

from .errors import LyricallyError

logger = logging.getLogger(__name__)


def create_db_path(storage_dir: str | Path | None = None) -> Path:
    """Determine and set up the storage directory for the database.

    Args:
        storage_dir: The desired path for database storage. Defaults to None.
    """
    try:
        if storage_dir is None:
            storage_dir_path = Path(platformdirs.user_data_dir("lyrically"))
            logger.debug(
                "No storage directory provided. Using default path: %s",
                storage_dir_path,
            )
        else:
            storage_dir_path = Path(storage_dir)
            logger.debug("Using provided storage directory: %s", storage_dir_path)

        # Create the directory and database path
        storage_dir_path.mkdir(parents=True, exist_ok=True)
        db_path = storage_dir_path / "lyrically.db"

        logger.debug("Database will be stored at: %s", db_path)

        return db_path
    except (OSError, PermissionError) as e:
        raise LyricallyError(f"Failed to create storage directory: {e}") from e
