import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)


@pytest.mark.asyncio
async def test_conversion_flow(mock_get_tickers, current_buda_tickers):
    """Test the complete flow with mocked API"""
    mock_get_tickers.return_value = current_buda_tickers

    moneda_destino = "PEN"

    response = client.get(
        f"/best-conversion?origin_currency=CLP&destination_currency={moneda_destino}&amount=1000"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monto"] == 3.84413311468126
    assert data["moneda_destino"] == moneda_destino
    assert data["moneda_intermediaria"] == "BTC"


@pytest.mark.asyncio
async def test_conversion_all_currency_pairs(mock_get_tickers, current_buda_tickers):
    """Test all possible currency pair combinations"""
    mock_get_tickers.return_value = current_buda_tickers
    currencies = ["CLP", "PEN", "COP"]
    for origin in currencies:
        for destination in currencies:
            if origin != destination:
                response = client.get(
                    f"/best-conversion?origin_currency={origin}&destination_currency={destination}&amount=1000"
                )
                assert response.status_code == 200
                data = response.json()
                assert data["monto"] > 0
                assert data["moneda_intermediaria"] is not None


@pytest.mark.asyncio
async def test_api_error_handling(mock_get_tickers):
    """Test error handling"""
    mock_get_tickers.side_effect = Exception("API Error")

    response = client.get(
        "/best-conversion?origin_currency=CLP&destination_currency=PEN&amount=1000"
    )
    assert response.status_code == 500
    assert (
        "An unexpected error occurred. Please try again later."
        in response.json()["detail"]
    )
