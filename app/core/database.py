"""
Database connection pool setup using the databases library.
Provides async query execution with connection pooling.
"""

import asyncpg
from contextlib import asynccontextmanager
from databases import Database

from app.core.config import settings


class DatabaseConnector:
    """Manages the database connection pool lifecycle."""

    def __init__(self):
        self.database = Database(
            settings.database_url,
            min_size=settings.db_min_pool_size,
            max_size=settings.db_max_pool_size,
        )

    async def connect(self):
        """Establish connection pool at app startup."""
        await self.database.connect()

    async def disconnect(self):
        """Close connection pool at app shutdown."""
        await self.database.disconnect()


# Global database instance
db_connector = DatabaseConnector()


@asynccontextmanager
async def get_database():
    """
    Dependency injection function for database.
    Yields the connected database instance.
    """
    yield db_connector.database
