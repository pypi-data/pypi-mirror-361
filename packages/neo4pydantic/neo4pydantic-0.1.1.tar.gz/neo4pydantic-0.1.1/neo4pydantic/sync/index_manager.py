from neo4j import Driver
from typing import Set, List
from ..core.index_registry import index_registry, Index
from ..exceptions import CreateIndexError

class IndexManager:
    """Manages index creation and synchronization"""

    def __init__(self, driver: "Driver"):
        self.driver = driver
        self._existing_indexes: Set[str] = set()

    def sync_indexes(self) -> List[str]:
        """Synchronize indexes with the database"""
        # Get existing indexes
        self._load_existing_indexes()

        # Create missing indexes
        return self._create_missing_indexes()

    def _load_existing_indexes(self):
        """Load existing indexes from database"""
        with self.driver.session() as session:
            result = session.run("SHOW INDEXES")
            self._existing_indexes = {record["name"] for record in result}

    def _create_missing_indexes(self) -> list[str]:
        """Create indexes that don't exist in database"""
        indexes = []
        for label, index_def, is_relationship in index_registry.get_all_indexes():
            index_identifier = index_def.name if index_def.name else f"index_{label}_{'_'.join(index_def.properties)}".lower()
            if index_identifier not in self._existing_indexes:
                self._create_index(label, index_def, is_relationship)
                indexes.append(index_identifier)

        return indexes

    def _create_index(self, label: str, index_def: Index, is_relationship: bool):
        """Create a single index"""
        try:
            cypher = index_def.generate_cypher(label, is_relationship)

            with self.driver.session() as session:
                session.run(cypher)

            index_registry.mark_created(index_def.name)

        except Exception as e:
            raise CreateIndexError(
                message="Error when create index",
                index_name=index_def.name,
                query=index_def.generate_cypher(label, is_relationship)
            ) from e
