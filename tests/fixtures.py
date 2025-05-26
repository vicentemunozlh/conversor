import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_tickers():
    return {
        "tickers": [
            {"market_id": "BTC-CLP", "last_price": ["1000000", "CLP"]},
            {"market_id": "BTC-PEN", "last_price": ["100000", "PEN"]},
            {"market_id": "BTC-COP", "last_price": ["2000000", "COP"]},
            {"market_id": "ETH-CLP", "last_price": ["1000000", "CLP"]},
            {"market_id": "ETH-PEN", "last_price": ["100000", "PEN"]},
            {"market_id": "ETH-COP", "last_price": ["2000000", "COP"]},
        ]
    }
