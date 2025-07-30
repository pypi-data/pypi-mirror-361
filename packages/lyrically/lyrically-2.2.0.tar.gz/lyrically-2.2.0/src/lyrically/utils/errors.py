class LyricallyError(Exception):
    """Base exception for all lyrically-related errors."""

    pass


class LyricallyDatabaseError(LyricallyError):
    """Base exception for database-related errors."""

    pass


class LyricallyConnectionError(LyricallyDatabaseError):
    """Raised when database connection fails."""

    pass


class LyricallyDataError(LyricallyDatabaseError):
    """Raised when database data insertion/retrieval fails."""

    pass
