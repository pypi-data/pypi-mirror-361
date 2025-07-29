from typing import Any, Dict, Optional, ClassVar, List
from pydantic import ConfigDict
from .custom_pydantic_base_model import CustomBaseModel


class BaseEntity(CustomBaseModel):
    """Base class for all Neo4j entities"""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    # Class-level configuration
    __label__: ClassVar[Optional[str]] = None
    __unique_fields__: ClassVar[List[str]] = []
    __indexed_fields__: ClassVar[List[str]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__label__ is None:
            cls.__label__ = cls.__name__

    @classmethod
    def get_label(cls) -> str:
        """Get the Neo4j label for this entity"""
        return cls.__label__ or cls.__name__

    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for Neo4j operations"""
        data = self.model_dump(exclude_none=exclude_none, by_alias=False)
        # Remove private fields
        return {k: v for k, v in data.items() if not k.startswith("_")}

    def get_unique_props(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Get unique props from Neo4j entity"""
        data = self.model_dump(exclude_none=exclude_none, by_alias=False)
        if self.__unique_fields__:
            return {k: v for k, v in data.items() if k in self.__unique_fields__}

        return {k: v for k, v in data.items() if not k.startswith("_")}

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "BaseEntity":
        """Create instance from Neo4j record"""
        return cls.model_validate(record)


class BaseNode(BaseEntity):
    """Base class for Neo4j nodes"""

    def get_create_query(self) -> tuple[str, Dict[str, Any]]:
        """Generate CREATE query for this node"""
        label = self.get_label()
        props = self.to_dict()

        if not props:
            return f"CREATE (n:{label})", {}

        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys())
        query = f"CREATE (n:{label} {{{prop_str}}})"
        return query, props

    def get_merge_query(self) -> tuple[str, Dict[str, Any]]:
        """Generate MERGE query for this node"""
        label = self.get_label()
        props = self.to_dict()

        if not self.__unique_fields__:
            raise ValueError(f"No unique fields defined for {self.__class__.__name__}")

        unique_props = {k: v for k, v in props.items() if k in self.__unique_fields__}
        other_props = {
            k: v for k, v in props.items() if k not in self.__unique_fields__
        }

        unique_str = ", ".join(f"{k}: ${k}" for k in unique_props.keys())
        query = f"MERGE (n:{label} {{{unique_str}}})"

        if other_props:
            set_str = ", ".join(f"n.{k} = ${k}" for k in other_props.keys())
            query += f" SET {set_str}"

        return query, props

    def get_find_query(self) -> tuple[str, Dict[str, Any]]:
        """Generate MATCH query to find this node"""
        label = self.get_label()
        props = self.to_dict()

        if not props:
            return f"MATCH (n:{label}) RETURN n", {}

        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys())
        query = f"MATCH (n:{label} {{{prop_str}}}) RETURN n"
        return query, props


class BaseRelationship(BaseEntity):
    """Base class for Neo4j relationships"""

    start_node: ClassVar["BaseNode"]
    __type__: ClassVar[Optional[str]] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__type__ is None:
            cls.__type__ = cls.__name__.upper()

    @classmethod
    def get_type(cls) -> str:
        """Get the Neo4j relationship type"""
        return cls.__type__ or cls.__name__.upper()

    def get_create_query(
        self, from_node_match: str, to_node_match: str
    ) -> tuple[str, Dict[str, Any]]:
        """Generate CREATE query for this relationship"""
        return self._get_relationship_generator_query(
            from_node_match, to_node_match, "CREATE"
        )

    def get_merge_query(
        self, from_node_match: str, to_node_match: str
    ) -> tuple[str, Dict[str, Any]]:
        """Generate MERGE query for this relationship"""
        return self._get_relationship_generator_query(
            from_node_match, to_node_match, "MERGE"
        )

    def _get_relationship_generator_query(
        self, from_node_match: str, to_node_match: str, generate_type: str = "CREATE"
    ) -> tuple[str, Dict[str, Any]]:
        rel_type = self.get_type()
        props = self.to_dict()

        if not props:
            query = f"MATCH {from_node_match}, {to_node_match} {generate_type} (a)-[r:{rel_type}]->(b)"
            return query, {}

        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys())
        query = f"MATCH {from_node_match}, {to_node_match} {generate_type} (a)-[r:{rel_type} {{{prop_str}}}]->(b)"
        return query, props
