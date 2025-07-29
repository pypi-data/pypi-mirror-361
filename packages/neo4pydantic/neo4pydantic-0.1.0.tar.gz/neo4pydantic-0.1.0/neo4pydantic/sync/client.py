from typing import Optional
from neo4j import GraphDatabase, Driver
from contextlib import contextmanager


class SyncClient:
    """Synchronous Neo4j client"""

    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        """Connect to Neo4j database"""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        """Close database connection"""
        if self._driver:
            self._driver.close()
            self._driver = None

    @contextmanager
    def session(self, **kwargs):
        """Context manager for database sessions"""
        driver = self.connect()
        session = driver.session(database=self.database, **kwargs)
        try:
            yield session
        finally:
            session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
