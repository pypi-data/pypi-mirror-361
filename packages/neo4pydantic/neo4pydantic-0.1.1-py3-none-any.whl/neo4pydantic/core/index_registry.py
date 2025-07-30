from enum import Enum
from typing import Dict, List, Set, Optional
from pydantic import BaseModel

class IndexType(Enum):
    """Types of indexes that can be created"""
    BTREE = "BTREE"
    TEXT = "TEXT"
    POINT = "POINT"
    RANGE = "RANGE"

class Index(BaseModel):
    """Represents an index definition"""
    name: Optional[str] = None
    properties: List[str] # add multiple value for composite index
    index_type: IndexType = IndexType.BTREE

    def generate_cypher(self, label: str, is_relationship: bool = False) -> str:
        """Generate Cypher query to create index"""
        index_name = self.name if self.name else f"index_{label}_{'_'.join(self.properties)}".lower()
        props = ", ".join(f"n.{prop}" for prop in self.properties)

        if is_relationship:
            pattern = f"()-[r:{label}]-()"
            props = ", ".join(f"r.{prop}" for prop in self.properties)
            if self.index_type == IndexType.TEXT:
                return f"CREATE TEXT INDEX {index_name} IF NOT EXISTS FOR {pattern} ON ({props})"
            else:
                return f"CREATE INDEX {index_name} IF NOT EXISTS FOR {pattern} ON ({props})"
        else:
            if self.index_type == IndexType.TEXT:
                return f"CREATE TEXT INDEX {index_name} IF NOT EXISTS FOR (n:{label}) ON ({props})"
            else:
                return f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:{label}) ON ({props})"

class IndexRegistry:
    """Track all indexes that need to be created"""

    def __init__(self):
        self._node_indexes: Dict[str, List[Index]] = {}
        self._relationship_indexes: Dict[str, List[Index]] = {}
        self._created_indexes: Set[str] = set()

    def register_node_indexes(self, label: str, indexes: List[Index]):
        """Register indexes for a node label"""
        if label not in self._node_indexes:
            self._node_indexes[label] = []
        self._node_indexes[label].extend(indexes)

    def register_relationship_indexes(self, relationship_type: str, indexes: List[Index]):
        """Register indexes for a relationship type"""
        if relationship_type not in self._relationship_indexes:
            self._relationship_indexes[relationship_type] = []
        self._relationship_indexes[relationship_type].extend(indexes)

    def get_all_indexes(self) -> List[tuple[str, Index, bool]]:
        """Get all registered indexes as (label/type, index_def, is_relationship)"""
        result = []

        for label, indexes in self._node_indexes.items():
            for index in indexes:
                result.append((label, index, False))

        for rel_type, indexes in self._relationship_indexes.items():
            for index in indexes:
                result.append((rel_type, index, True))

        return result

    def mark_created(self, index_name: str):
        """Mark an index as created"""
        self._created_indexes.add(index_name)

    def is_created(self, index_name: str) -> bool:
        """Check if an index has been created"""
        return index_name in self._created_indexes

# Global entrypoint for index registry
index_registry = IndexRegistry()
