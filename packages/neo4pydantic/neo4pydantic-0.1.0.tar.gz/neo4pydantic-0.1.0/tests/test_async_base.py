import pytest
from neo4pydantic.async_ import base
from unittest.mock import AsyncMock, MagicMock


class DummyNode(base.BaseNode):
    __label__ = "Dummy"
    __unique_fields__ = ["id"]
    id: int
    name: str


class DummyRelationship(base.BaseRelationship):
    __type__ = "DUMMY_REL"
    prop: str


@pytest.mark.asyncio
async def test_save_node_merges_on_unique():
    session = AsyncMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single = AsyncMock(
        return_value={"n": {"id": 1, "name": "foo"}}
    )
    result = await node.save(session)
    assert isinstance(result, DummyNode)
    assert result.id == 1 and result.name == "foo"
    session.run.assert_called()


@pytest.mark.asyncio
async def test_save_node_returns_self_on_no_record():
    session = AsyncMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single = AsyncMock(return_value=None)
    result = await node.save(session)
    assert result is node


@pytest.mark.asyncio
async def test_delete_node_success():
    session = AsyncMock()
    node = DummyNode(id=1, name="foo")
    summary = MagicMock()
    summary.counters.nodes_deleted = 1
    session.run.return_value.consume = AsyncMock(return_value=summary)
    result = await node.delete(session)
    assert result is True


@pytest.mark.asyncio
async def test_delete_node_failure():
    session = AsyncMock()
    node = DummyNode(id=1, name="foo")
    summary = MagicMock()
    summary.counters.nodes_deleted = 0
    session.run.return_value.consume = AsyncMock(return_value=summary)
    result = await node.delete(session)
    assert result is False


@pytest.mark.asyncio
async def test_refresh_node_found():
    session = AsyncMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single = AsyncMock(
        return_value={"n": {"id": 1, "name": "foo"}}
    )
    result = await node.refresh(session)
    assert isinstance(result, DummyNode)
    assert result.id == 1


@pytest.mark.asyncio
async def test_refresh_node_not_found():
    session = AsyncMock()
    node = DummyNode(id=1, name="foo")
    session.run.return_value.single = AsyncMock(return_value=None)
    result = await node.refresh(session)
    assert result is None


@pytest.mark.asyncio
async def test_find_by_nodes():
    session = AsyncMock()
    session.run.return_value.data = AsyncMock(
        return_value=[{"n": {"id": 1, "name": "foo"}}, {"n": {"id": 2, "name": "bar"}}]
    )
    nodes = await DummyNode.find_by(session, name="foo")
    assert len(nodes) == 2
    assert all(isinstance(n, DummyNode) for n in nodes)


@pytest.mark.asyncio
async def test_find_one_by_node():
    session = AsyncMock()
    session.run.return_value.data = AsyncMock(
        return_value=[{"n": {"id": 1, "name": "foo"}}]
    )
    node = await DummyNode.find_one_by(session, name="foo")
    assert isinstance(node, DummyNode)
    assert node.name == "foo"


@pytest.mark.asyncio
async def test_find_one_by_node_none():
    session = AsyncMock()
    session.run.return_value.data = AsyncMock(return_value=[])
    node = await DummyNode.find_one_by(session, name="foo")
    assert node is None


class TestAsyncBaseRelationship:
    @pytest.mark.asyncio
    async def test_save(self):
        session = AsyncMock()
        from_node = DummyNode(id=1, name="foo")
        to_node = DummyNode(id=2, name="bar")
        rel = DummyRelationship(prop="baz")
        session.run.return_value.consume = AsyncMock()
        result = await rel.save(session, from_node, to_node)
        assert result is rel
        session.run.assert_called()

    @pytest.mark.asyncio
    async def test_save_with_custom_params(self):
        session = AsyncMock()
        rel = DummyRelationship(prop="baz")
        session.run.return_value.consume = AsyncMock()
        result = await rel.save_with_custom_params(
            session,
            from_node_label="Dummy",
            to_node_label="Dummy",
            from_node_params={"id": 1},
            to_node_params={"id": 2},
        )
        assert result is rel
        session.run.assert_called()
