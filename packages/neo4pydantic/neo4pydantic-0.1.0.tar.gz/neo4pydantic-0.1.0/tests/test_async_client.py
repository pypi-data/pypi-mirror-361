import pytest
from neo4pydantic.async_ import client
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_connect_creates_driver():
    with patch(
        "neo4j_models.async_.client.AsyncGraphDatabase.driver", new_callable=MagicMock
    ) as mock_driver:
        driver = MagicMock()
        mock_driver.return_value = driver
        c = client.AsyncClient("bolt://localhost", "user", "pass")
        res = await c.connect()
        assert c._driver is driver
        assert res is driver
        mock_driver.assert_called_once_with("bolt://localhost", auth=("user", "pass"))


@pytest.mark.asyncio
async def test_connect_reuses_existing_driver():
    c = client.AsyncClient("bolt://localhost", "user", "pass")
    c._driver = MagicMock()
    res = await c.connect()
    assert res is c._driver


@pytest.mark.asyncio
async def test_close_closes_driver():
    c = client.AsyncClient("bolt://localhost", "user", "pass")
    mock_driver = AsyncMock()
    c._driver = mock_driver
    await c.close()
    mock_driver.close.assert_awaited_once()
    assert c._driver is None


@pytest.mark.asyncio
async def test_close_no_driver():
    c = client.AsyncClient("bolt://localhost", "user", "pass")
    c._driver = None
    await c.close()


@pytest.mark.asyncio
async def test_async_context_manager():
    c = client.AsyncClient("bolt://localhost", "user", "pass")
    c.close = AsyncMock()
    async with c as inst:
        assert inst is c
    c.close.assert_awaited_once()
