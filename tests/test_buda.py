import pytest
from app.api.services.buda import get_most_destination_crypto_from_amount


@pytest.mark.asyncio
async def test_direct_conversion(mock_get_tickers):
    # Set the return value for this specific test
    mock_get_tickers.return_value = {
        "tickers": [
            {"market_id": "COP-CLP", "last_price": ["0.0025", "CLP"]},
            {"market_id": "PEN-COP", "last_price": ["400", "CLP"]},
        ]
    }

    amount, intermediary = await get_most_destination_crypto_from_amount(
        "CLP", "COP", 1000.0
    )
    assert amount == 2.5  # 1000 * 0.0025
    assert intermediary is None


@pytest.mark.asyncio
async def test_conversion_with_intermediary(mock_get_tickers):
    # Different return value for this test
    mock_get_tickers.return_value = {
        "tickers": [
            {"market_id": "CLP-PEN", "last_price": ["0.0025", "PEN"]},
            {"market_id": "PEN-COP", "last_price": ["1.6", "COP"]},
        ]
    }

    amount, intermediary = await get_most_destination_crypto_from_amount(
        "CLP", "COP", 1000.0
    )
    assert amount == 4.0  # 1000 * 0.0025 * 1.6
    assert intermediary == "PEN"


@pytest.mark.asyncio
async def test_no_conversion_path(mock_get_tickers):
    # Empty tickers for this test
    mock_get_tickers.return_value = {
        "tickers": [
            {"market_id": "BTC-ETH", "last_price": ["0.0025", "ETH"]},
            {"market_id": "ETH-BTC", "last_price": ["1.6", "BTC"]},
        ]
    }

    amount, intermediary = await get_most_destination_crypto_from_amount(
        "INVALID", "ALSO_INVALID", 1000.0
    )
    assert amount is None
    assert intermediary is None


@pytest.mark.asyncio
async def test_api_error(mock_get_tickers):
    # Set error for this test
    mock_get_tickers.side_effect = Exception("API Error")

    with pytest.raises(Exception) as exc_info:
        await get_most_destination_crypto_from_amount("CLP", "PEN", 1000.0)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_conversion_with_intermediary_realistic_values(mock_get_tickers):
    # Different return value for this test
    mock_get_tickers.return_value = _current_buda_tickers()

    amount, intermediary = await get_most_destination_crypto_from_amount(
        "CLP", "COP", 1000.0
    )
    assert amount == 4377.842500094991  # 1000 * 1/2421284.0 * 10600000.0
    assert intermediary == "ETH"


# This are some of the current tickers from Buda API. 26/05/2025
def _current_buda_tickers():
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
