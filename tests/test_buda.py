import pytest
from app.api.services.buda import get_most_destination_currency_from_amount


@pytest.mark.asyncio
async def test_conversion_with_intermediary(mock_get_tickers):
    # Different return value for this test
    mock_get_tickers.return_value = {
        "tickers": [
            {"market_id": "BTC-CLP", "last_price": ["100", "CLP"]},
            {"market_id": "BTC-COP", "last_price": ["400", "COP"]},
        ]
    }

    amount, intermediary = await get_most_destination_currency_from_amount(
        "CLP", "COP", 1000.0
    )
    assert amount == 4000.0  # 1000 * 1/100 * 400
    assert intermediary == "BTC"


@pytest.mark.asyncio
async def test_no_conversion_path(mock_get_tickers):
    # Empty tickers for this test
    mock_get_tickers.return_value = {
        "tickers": [
            {"market_id": "BTC-ETH", "last_price": ["0.0025", "ETH"]},
            {"market_id": "ETH-BTC", "last_price": ["1.6", "BTC"]},
        ]
    }

    amount, intermediary = await get_most_destination_currency_from_amount(
        "INVALID", "ALSO_INVALID", 1000.0
    )
    assert amount is None
    assert intermediary is None


@pytest.mark.asyncio
async def test_api_error(mock_get_tickers):
    # Set error for this test
    mock_get_tickers.side_effect = Exception("API Error")

    with pytest.raises(Exception) as exc_info:
        await get_most_destination_currency_from_amount("CLP", "PEN", 1000.0)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_conversion_with_intermediary_realistic_values(
    mock_get_tickers, current_buda_tickers
):
    mock_get_tickers.return_value = current_buda_tickers

    amount, intermediary = await get_most_destination_currency_from_amount(
        "CLP", "COP", 1000.0
    )
    assert amount == 4377.842500094991  # 1000 * 1/2421284.0 * 10600000.0
    assert intermediary == "ETH"


@pytest.mark.asyncio
async def test_api_response_not_expected(mock_get_tickers):
    mock_get_tickers.return_value = {
        "tickers": [
            {"market_id": "BTC-CLP", "last_price": ["100", "BTC"]},
            {"market_id": "BTC-COP", "last_price": ["400", "BTC"]},
        ]
    }

    with pytest.raises(ValueError) as exc_info:
        await get_most_destination_currency_from_amount("CLP", "COP", 1000.0)
    assert "The unit of the last_price is not the same as the origin_currency" in str(
        exc_info.value
    )
