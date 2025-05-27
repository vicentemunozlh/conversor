import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_conversion():
    with patch("app.api.routes.get_most_destination_crypto_from_amount") as mock:
        yield mock


@pytest.fixture
def mock_get_tickers():
    """Fixture to mock _get_all_tickers, allowing return value to be set in tests"""
    with patch(
        "app.api.services.buda._get_all_tickers", new_callable=AsyncMock
    ) as mock:
        yield mock
