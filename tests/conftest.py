import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_conversion():
    with patch("app.api.routes.get_most_destination_currency_from_amount") as mock:
        yield mock


@pytest.fixture
def mock_get_tickers():
    """Fixture to mock _get_all_tickers, allowing return value to be set in tests"""
    with patch(
        "app.api.services.buda._get_all_tickers", new_callable=AsyncMock
    ) as mock:
        yield mock


# This are some of the current tickers from Buda API. 26/05/2025
@pytest.fixture
def current_buda_tickers():
    return {
        "tickers": [
            {"market_id": "BTC-CLP", "last_price": ["102558064.0", "CLP"]},
            {"market_id": "BTC-PEN", "last_price": ["394246.85", "PEN"]},
            {"market_id": "BTC-COP", "last_price": ["444009380.34", "COP"]},
            {"market_id": "ETH-CLP", "last_price": ["2421284.0", "CLP"]},
            {"market_id": "ETH-PEN", "last_price": ["9191.78", "PEN"]},
            {"market_id": "ETH-COP", "last_price": ["10600000.0", "COP"]},
        ]
    }
