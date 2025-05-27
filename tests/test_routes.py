from fastapi.testclient import TestClient
from app.main import app
import httpx

client = TestClient(app)


def test_best_conversion_success(client, mock_conversion):
    # Mock the conversion function to return a successful result
    mock_conversion.return_value = (1000.0, "BTC")

    response = client.get(
        "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=1000"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["monto"] == 1000.0
    assert data["moneda_destino"] == "PEN"
    assert data["moneda_intermediaria"] == "BTC"


def test_best_conversion_no_path(client, mock_conversion):
    # Mock the conversion function to return no path found
    mock_conversion.return_value = (None, None)

    response = client.get(
        "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=1000"
    )

    assert response.status_code == 404
    assert "No conversion path found" in response.json()["detail"]


def test_best_conversion_invalid_currency(client, mock_conversion):
    # We will call the endpoint with an invalid currency
    invalid_currency = "INVALID"
    response = client.get(
        "/best-conversion?origin_crypto="
        + invalid_currency
        + "&destination_crypto=PEN&amount=1000"
    )
    assert response.status_code == 422  # Validation error

    # Verify that the mock was never called
    mock_conversion.assert_not_called()

    # Get the error details from the response
    error_details = response.json()

    # Check only the essential parts of the error
    error = error_details["detail"][0]
    assert error["input"] == "INVALID"
    assert error["loc"] == ["query", "origin_crypto"]
    assert error["msg"] == "Input should be 'CLP', 'PEN' or 'COP'"
    assert "expected" in error["ctx"]


def test_best_conversion_invalid_amount(client, mock_conversion):
    # We will call the endpoint with an invalid amount
    invalid_amount = -1000
    response = client.get(
        "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount="
        + str(invalid_amount)
    )
    assert response.status_code == 422  # Validation error

    # Verify that the mock was never called
    mock_conversion.assert_not_called()

    error_details = response.json()
    error = error_details["detail"][0]

    # Check the correct error message for negative amount
    assert error["msg"] == "Input should be greater than 0"
    assert error["input"] == "-1000"
    assert error["loc"] == ["query", "amount"]
    assert error["type"] == "greater_than"


def test_best_conversion_endpoint_returns_500_for_other_errors(client, mock_conversion):
    # Mock the conversion function to raise an exception
    mock_conversion.side_effect = Exception("Test exception")

    response = client.get(
        "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=1000"
    )
    assert response.status_code == 500
    assert (
        "Unexpected error processing conversion: Test exception"
        in response.json()["detail"]
    )


def test_best_conversion_external_api_error(client, mock_conversion):
    # Test HTTP client error
    mock_conversion.side_effect = httpx.HTTPError("Connection failed")

    response = client.get(
        "/best-conversion?origin_crypto=CLP&destination_crypto=PEN&amount=1000"
    )

    assert response.status_code == 500
    assert "Service temporarily unavailable" in response.json()["detail"]
