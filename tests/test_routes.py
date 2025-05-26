import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_best_conversion_success():
    with patch(
        "app.api.services.buda.get_most_destination_crypto_from_amount"
    ) as mock_get_conversion:
        # Mock the conversion function to return a successful result
        mock_get_conversion.return_value = (1000.0, "BTC")

        response = client.get(
            "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=1000"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["monto"] == 1000.0
        assert data["moneda_destino"] == "PEN"
        assert data["moneda_intermediaria"] == "BTC"


def test_best_conversion_no_path():
    with patch(
        "app.api.services.buda.get_most_destination_crypto_from_amount"
    ) as mock_get_conversion:
        # Mock the conversion function to return no path found
        mock_get_conversion.return_value = (None, None)

        response = client.get(
            "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=1000"
        )

        assert response.status_code == 404
        assert "No conversion path found" in response.json()["detail"]


def test_best_conversion_invalid_currency():
    response = client.get(
        "/best-conversion?origin_crypto=INVALID&destination_crypto=PEN&amount=1000"
    )
    assert response.status_code == 422  # Validation error


def test_best_conversion_invalid_amount():
    response = client.get(
        "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=-1000"
    )
    assert response.status_code == 422  # Validation error
