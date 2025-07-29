from os import getenv
from abc import ABC, abstractmethod
from typing import Any, ContextManager

class DBClientBase(ABC):
    """Abstract base class for database clients."""
    def __init__(self):
        user = getenv("POSTGRES_USER")
        password = getenv("POSTGRES_PASSWORD")
        host = getenv("POSTGRES_HOST", "localhost")
        port = getenv("POSTGRES_PORT", "5432")
        dbname = getenv("POSTGRES_DB")

        if not all([user, password, dbname]):
            raise EnvironmentError("Missing required PostgreSQL environment variables")

        self.connection_params = {
            "host": host,
            "port": port,
            "dbname": dbname,
            "user": user,
            "password": password
        }
        
    @abstractmethod
    def __init__(self) -> None:
        """Initialize the database client with connection parameters."""

    @abstractmethod
    def scoped_session(self) -> ContextManager[Any]:
        """Context manager for scoped database operations with auto commit/rollback/close."""

    @abstractmethod
    def get_persistent_session(self) -> Any:
        """Get a persistent session/connection that caller must manage."""
