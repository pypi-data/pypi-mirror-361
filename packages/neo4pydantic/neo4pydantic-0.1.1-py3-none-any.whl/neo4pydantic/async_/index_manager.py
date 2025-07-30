from neo4j import AsyncDriver
from typing import Set, List
from ..core.index_registry import index_registry, Index
from ..exceptions import CreateIndexError

class IndexManager:
    """Manages index creation and synchronization"""

    def __init__(self, driver: "AsyncDriver"):
        self.driver = driver
        self._existing_indexes: Set[str] = set()

    async def sync_indexes(self) -> List[str]:
        """Synchronize indexes with the database"""
        await self._load_existing_indexes()
        return await self._create_missing_indexes()

    async def _load_existing_indexes(self):
        """Load existing indexes from database"""
        async with self.driver.session() as session:
            result = await session.run("SHOW INDEXES")
            data = await result.data()
            self._existing_indexes = {record["name"] for record in data}

    async def _create_missing_indexes(self) -> List[str]:
        """Create indexes that don't exist in database"""
        indexes = []
        for label, index_def, is_relationship in index_registry.get_all_indexes():
            index_identifier = index_def.name if index_def.name else f"index_{label}_{'_'.join(index_def.properties)}".lower()
            if index_identifier not in self._existing_indexes:
                await self._create_index(label, index_def, is_relationship)
                indexes.append(index_identifier)

        return indexes

    async def _create_index(self, label: str, index_def: Index, is_relationship: bool):
        """Create a single index"""
        try:
            cypher = index_def.generate_cypher(label, is_relationship)

            async with self.driver.session() as session:
                await session.run(cypher)

            index_registry.mark_created(index_def.name)

        except Exception as e:
            raise CreateIndexError(
                message="Error when create index",
                index_name=index_def.name,
                query=index_def.generate_cypher(label, is_relationship)
            ) from e
