from typing import Optional, List
from neo4j import Session
from ..core.base import (
    BaseNode as CoreBaseNode,
    BaseRelationship as CoreBaseRelationship,
)


class BaseNode(CoreBaseNode):
    """Synchronous Neo4j node operations"""

    def save(self, session: Session) -> "BaseNode":
        """Save node to Neo4j database"""
        if self.__unique_fields__:
            query, params = self.get_merge_query()
        else:
            query, params = self.get_create_query()

        result = session.run(query, params)
        record = result.single()

        if record and "n" in record:
            node_data = dict(record["n"])
            return self.from_record(node_data)

        return self

    def delete(self, session: Session) -> bool:
        """Delete node from Neo4j database"""
        query, params = self.get_find_query()
        delete_query = query.replace("RETURN n", "DELETE n")

        result = session.run(delete_query, params)
        return result.consume().counters.nodes_deleted > 0

    def refresh(self, session: Session) -> Optional["BaseNode"]:
        """Refresh node data from database"""
        query, params = self.get_find_query()
        result = session.run(query, params)
        record = result.single()

        if record and "n" in record:
            node_data = dict(record["n"])
            return self.from_record(node_data)

        return None

    @classmethod
    def find_by(
        cls,
        session: Session,
        pagination_mode: bool = False,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        **kwargs,
    ) -> List["BaseNode"]:
        """Find nodes by properties with optional pagination"""
        label = cls.get_label()

        if not kwargs:
            query = f"MATCH (n:{label})"
            params = {}
        else:
            prop_str = ", ".join(f"{k}: ${k}" for k in kwargs.keys())
            query = f"MATCH (n:{label} {{{prop_str}}})"
            params = kwargs

        query += " RETURN n"

        if pagination_mode:
            query += " SKIP $skip LIMIT $limit"
            params["skip"] = skip
            params["limit"] = limit

        result = session.run(query, params)
        return [cls.from_record(dict(record["n"])) for record in result]

    @classmethod
    def find_one_by(cls, session: Session, **kwargs) -> Optional["BaseNode"]:
        """Find single node by properties"""
        nodes = cls.find_by(session, **kwargs)
        return nodes[0] if nodes else None


class BaseRelationship(CoreBaseRelationship):
    """Synchronous Neo4j relationship operations"""

    def save(
        self, session: Session, from_node: BaseNode, to_node: BaseNode
    ) -> "BaseRelationship":
        """Save relationship between two nodes"""
        from_label = from_node.get_label()
        to_label = to_node.get_label()

        from_props = from_node.get_unique_props()
        to_props = to_node.get_unique_props()

        return self._save_relationship(
            session, from_label, to_label, from_props, to_props
        )

    def save_with_custom_params(
        self,
        session: Session,
        from_node_label: str,
        to_node_label: str,
        from_node_params: dict | None = None,
        to_node_params: dict | None = None,
    ):
        """Save relationship with custom params, use this when"""
        return self._save_relationship(
            session, from_node_label, to_node_label, from_node_params, to_node_params
        )

    def _save_relationship(
        self,
        session: Session,
        from_node_label: str,
        to_node_label: str,
        from_node_params: dict | None = None,
        to_node_params: dict | None = None,
    ):
        if from_node_params:
            from_prop_str = ", ".join(
                f"{k}: $from_{k}" for k in from_node_params.keys()
            )
            from_match = f"(a:{from_node_label} {{{from_prop_str}}})"
        else:
            from_match = f"(a:{from_node_label})"

        if to_node_params:
            to_prop_str = ", ".join(f"{k}: $to_{k}" for k in to_node_params.keys())
            to_match = f"(b:{to_node_label} {{{to_prop_str}}})"
        else:
            to_match = f"(b:{to_node_label})"

        query, rel_params = self.get_create_query(from_match, to_match)

        # Combine parameters
        params = {}
        params.update({f"from_{k}": v for k, v in from_node_params.items()})
        params.update({f"to_{k}": v for k, v in to_node_params.items()})
        params.update(rel_params)

        result = session.run(query, params)
        result.consume()

        return self
