from neo4pydantic.core import base


class DummyEntity(base.BaseEntity):
    __label__ = "DummyEntity"
    __unique_fields__ = ["id"]
    id: int
    name: str


class DummyNode(base.BaseNode):
    __label__ = "DummyNode"
    __unique_fields__ = ["id"]
    id: int
    name: str


class DummyRelationship(base.BaseRelationship):
    __type__ = "DUMMY_REL"
    prop: str


def test_to_dict():
    e = DummyEntity(id=1, name="foo")
    d = e.to_dict()
    assert d == {"id": 1, "name": "foo"}


def test_get_label():
    assert DummyEntity.get_label() == "DummyEntity"
    assert DummyNode.get_label() == "DummyNode"


def test_from_record():
    rec = {"id": 2, "name": "bar"}
    e = DummyEntity.from_record(rec)
    assert isinstance(e, DummyEntity)
    assert e.id == 2 and e.name == "bar"


def test_get_create_query():
    n = DummyNode(id=1, name="foo")
    query, params = n.get_create_query()
    assert query.startswith("CREATE (n:DummyNode")
    assert params == {"id": 1, "name": "foo"}


def test_get_merge_query():
    n = DummyNode(id=1, name="foo")
    query, params = n.get_merge_query()
    assert query.startswith("MERGE (n:DummyNode")
    assert "SET n.name = $name" in query
    assert params == {"id": 1, "name": "foo"}


def test_get_find_query():
    n = DummyNode(id=1, name="foo")
    query, params = n.get_find_query()
    assert query.startswith("MATCH (n:DummyNode")
    assert "RETURN n" in query
    assert params == {"id": 1, "name": "foo"}


def test_relationship_get_create_query():
    rel = DummyRelationship(prop="baz")
    query, params = rel.get_create_query(
        "(a:DummyNode {id: $from_id})", "(b:DummyNode {id: $to_id})"
    )
    assert query.startswith(
        "MATCH (a:DummyNode {id: $from_id}), (b:DummyNode {id: $to_id}) CREATE (a)-[r:DUMMY_REL"
    )
    assert params == {"prop": "baz"}


def test_relationship_get_merge_query():
    rel = DummyRelationship(prop="baz")
    query, params = rel.get_merge_query(
        "(a:DummyNode {id: $from_id})", "(b:DummyNode {id: $to_id})"
    )
    assert query.startswith(
        "MATCH (a:DummyNode {id: $from_id}), (b:DummyNode {id: $to_id}) MERGE (a)-[r:DUMMY_REL"
    )
    assert params == {"prop": "baz"}
