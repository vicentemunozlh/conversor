from fastapi import HTTPException
import httpx
from typing import Optional


async def _call_external_api(url: str, params: Optional[dict] = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            status_code = getattr(e, "response", None)
            status_code = status_code.status_code if status_code else 500
            raise HTTPException(
                status_code=status_code, detail=f"External API error: {str(e)}"
            )


async def _get_all_tickers():
    url = "https://www.buda.com/api/v2/tickers"
    return await _call_external_api(url)


async def get_most_destination_currency_from_amount(
    origin_currency: str, destination_currency: str, amount: float
):
    """
    Convert between fiat currencies (CLP, PEN, COP) using cryptocurrency markets as intermediaries.
    Note: There are no direct markets between fiat currencies, so all conversions will use
    cryptocurrency markets (like BTC-CLP, ETH-PEN, etc.) as intermediaries.
    """
    tickers = await _get_all_tickers()
    # We store the tickers in a dictionary for O(1) lookup time.
    tickers_dict = {}

    for ticker in tickers["tickers"]:
        # Store tickers in a dictionary for O(1) lookup time.
        tickers_dict[ticker["market_id"]] = ticker["last_price"]

    best_rate = None
    best_intermediary = None

    for market_id, last_price in tickers_dict.items():
        # Split the market_id to get the currencies
        base, quote = market_id.split("-")
        intermediary = None

        # We need to see if the from currency is part of the market_id.
        if quote == origin_currency:
            intermediary = base
        else:
            continue

        # Calculate the amount of the intermediary currency from the from_amount.
        intermediary_amount = _buy_intermediate_crypto(
            last_price, amount, origin_currency
        )

        # We need to see if the intermediary currency and the destination_currency have a market_id.
        final_market_id = f"{intermediary}-{destination_currency}"
        if final_market_id in tickers_dict:
            possible_rate = _sell_intermediate_crypto(
                tickers_dict[final_market_id], intermediary_amount, destination_currency
            )
        else:
            # If the final_market_id is not in the tickers_dict, we continue to the next market_id.
            continue

        # We update the final_amount if its better than the current best_rate.
        # And update the best intermediary
        if best_rate is None or possible_rate > best_rate:
            best_rate = possible_rate
            best_intermediary = intermediary

    return best_rate, best_intermediary


def _buy_intermediate_crypto(
    last_price: list, currency_amount: float, origin_currency: str
):
    price = last_price[0]
    unit = last_price[1]
    if unit != origin_currency:
        raise ValueError(
            f"The unit of the last_price is not the same as the origin_currency. {unit} != {origin_currency}"
        )
    return currency_amount / float(price)


def _sell_intermediate_crypto(
    last_price: list, crypto_amount: float, destination_currency: str
):
    price = last_price[0]
    unit = last_price[1]
    if unit != destination_currency:
        raise ValueError(
            f"The unit of the last_price is not the same as the origin_currency. {unit} != {destination_currency}"
        )
    return crypto_amount * float(price)
