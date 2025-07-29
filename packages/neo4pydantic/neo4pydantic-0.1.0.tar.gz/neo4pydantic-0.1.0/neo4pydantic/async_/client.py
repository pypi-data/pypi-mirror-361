from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from contextlib import asynccontextmanager


class AsyncClient:
    """Asynchronous Neo4j client"""

    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver: Optional[AsyncDriver] = None

    async def connect(self) -> AsyncDriver:
        """Connect to Neo4j database"""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
        return self._driver

    async def close(self):
        """Close database connection"""
        if self._driver:
            await self._driver.close()
            self._driver = None

    @asynccontextmanager
    async def session(self, **kwargs):
        """Context manager for database sessions"""
        driver = await self.connect()
        session = driver.session(database=self.database, **kwargs)
        try:
            yield session
        finally:
            await session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
