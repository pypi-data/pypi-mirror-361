from neo4pydantic.sync import client
from unittest.mock import patch, MagicMock


def test_connect_creates_driver():
    with patch(
        "neo4j_models.sync.client.GraphDatabase.driver", new_callable=MagicMock
    ) as mock_driver:
        driver = MagicMock()
        mock_driver.return_value = driver
        c = client.SyncClient("bolt://localhost", "user", "pass")
        res = c.connect()
        assert c._driver is driver
        assert res is driver
        mock_driver.assert_called_once_with("bolt://localhost", auth=("user", "pass"))


def test_connect_reuses_existing_driver():
    c = client.SyncClient("bolt://localhost", "user", "pass")
    c._driver = MagicMock()
    res = c.connect()
    assert res is c._driver


def test_close_closes_driver():
    c = client.SyncClient("bolt://localhost", "user", "pass")
    mock_driver = MagicMock()
    c._driver = mock_driver
    c.close()
    mock_driver.close.assert_called_once()
    assert c._driver is None


def test_close_no_driver():
    c = client.SyncClient("bolt://localhost", "user", "pass")
    c._driver = None
    c.close()  # Should not raise


def test_session_context_manager():
    c = client.SyncClient("bolt://localhost", "user", "pass")
    mock_driver = MagicMock()
    mock_session = MagicMock()
    c._driver = mock_driver
    mock_driver.session.return_value = mock_session
    with c.session() as session:
        assert session is mock_session
    mock_session.close.assert_called_once()


def test_context_manager():
    c = client.SyncClient("bolt://localhost", "user", "pass")
    c.close = MagicMock()
    with c as inst:
        assert inst is c
    c.close.assert_called_once()
