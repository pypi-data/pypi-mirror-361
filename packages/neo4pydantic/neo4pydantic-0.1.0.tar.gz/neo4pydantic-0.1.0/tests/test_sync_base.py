from neo4pydantic.sync import base
from unittest.mock import MagicMock


class DummyNode(base.BaseNode):
    __label__ = "DummyNode"
    __unique_fields__ = ["id"]
    id: int
    name: str


class DummyRelationship(base.BaseRelationship):
    __type__ = "DUMMY_REL"
    prop: str


def test_save_node_merges_on_unique():
    session = MagicMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single.return_value = {"n": {"id": 1, "name": "foo"}}
    result = node.save(session)
    assert isinstance(result, DummyNode)
    assert result.id == 1 and result.name == "foo"
    session.run.assert_called()


def test_save_node_returns_self_on_no_record():
    session = MagicMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single.return_value = None
    result = node.save(session)
    assert result is node


def test_delete_node_success():
    session = MagicMock()
    node = DummyNode(id=1, name="foo")
    summary = MagicMock()
    summary.counters.nodes_deleted = 1
    session.run.return_value.consume.return_value = summary
    result = node.delete(session)
    assert result is True


def test_delete_node_failure():
    session = MagicMock()
    node = DummyNode(id=1, name="foo")
    summary = MagicMock()
    summary.counters.nodes_deleted = 0
    session.run.return_value.consume.return_value = summary
    result = node.delete(session)
    assert result is False


def test_refresh_node_found():
    session = MagicMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single.return_value = {"n": {"id": 1, "name": "foo"}}
    result = node.refresh(session)
    assert isinstance(result, DummyNode)
    assert result.id == 1


def test_refresh_node_not_found():
    session = MagicMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single.return_value = None
    result = node.refresh(session)
    assert result is None


def test_find_by_nodes():
    session = MagicMock()
    session.run.return_value = [
        MagicMock(
            **{
                "__getitem__.side_effect": lambda k: {"id": 1, "name": "foo"}
                if k == "n"
                else None
            }
        ),
        MagicMock(
            **{
                "__getitem__.side_effect": lambda k: {"id": 2, "name": "bar"}
                if k == "n"
                else None
            }
        ),
    ]
    nodes = DummyNode.find_by(session, name="foo")
    assert len(nodes) == 2
    assert all(isinstance(n, DummyNode) for n in nodes)


def test_find_one_by_node():
    session = MagicMock()
    session.run.return_value = [
        MagicMock(
            **{
                "__getitem__.side_effect": lambda k: {"id": 1, "name": "foo"}
                if k == "n"
                else None
            }
        ),
    ]
    node = DummyNode.find_one_by(session, name="foo")
    assert isinstance(node, DummyNode)
    assert node.name == "foo"


def test_find_one_by_node_none():
    session = MagicMock()
    session.run.return_value = []
    node = DummyNode.find_one_by(session, name="foo")
    assert node is None


def test_relationship_save():
    session = MagicMock()
    from_node = DummyNode(id=1, name="foo")
    to_node = DummyNode(id=2, name="bar")
    rel = DummyRelationship(prop="baz")
    session.run.return_value.consume.return_value = None
    result = rel.save(session, from_node, to_node)
    assert result is rel
    session.run.assert_called()


def test_relationship_save_with_custom_params():
    session = MagicMock()
    rel = DummyRelationship(prop="baz")
    session.run.return_value.consume.return_value = None
    result = rel.save_with_custom_params(
        session,
        from_node_label="DummyNode",
        to_node_label="DummyNode",
        from_node_params={"id": 1},
        to_node_params={"id": 2},
    )
    assert result is rel
    session.run.assert_called()
