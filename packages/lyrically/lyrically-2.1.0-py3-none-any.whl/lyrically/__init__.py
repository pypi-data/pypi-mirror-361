import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Lyrically:
    """A Python client for scraping artist lyrical discographies.

    This library provides an asynchronous interface to retrieve complete
    artist discographies from AZLyrics, including album metadata and song
    lyrics, with built-in database storage, proxy support, and robust error
    handling.
    """

    def __init__(self) -> None:
        """Initialize the Lyrically instance."""
        logger.info("Lyrically instance has been initialized.")
