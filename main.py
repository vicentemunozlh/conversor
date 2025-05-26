from typing import Union
from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

# Supuestos:
# - Case sensitive for the currencies, we expect the currencies to be in uppercase.
# - No se considera el minimum_order_amount

app = FastAPI()


class Currency(str, Enum):
    CLP = "CLP"
    PEN = "PEN"
    COP = "COP"


@app.get(
    "/best-conversion",
    summary="Obtener la mejor tasa de conversión entre monedas",
    description="""
    Convierte entre las monedas CLP, PEN y COP usando la mejor tasa disponible.
    
    **IMPORTANTE**: Las monedas deben ser ingresadas en MAYÚSCULAS (CLP, PEN, COP).
    """,
)
async def best_conversion(
    origin_crypto: Currency = Query(
        ..., description="Moneda de origen (debe ser CLP, PEN o COP en MAYÚSCULAS)"
    ),
    destination_crypto: Currency = Query(
        ..., description="Moneda de destino (debe ser CLP, PEN o COP en MAYÚSCULAS)"
    ),
    amount: float = Query(..., description="Monto a convertir de la moneda de origen"),
):
    try:
        final_amount, intermediary = await get_most_destination_crypto_from_amount(
            origin_crypto, destination_crypto, amount
        )
        if final_amount is None:
            raise HTTPException(
                status_code=404,
                detail=f"No conversion path found for {origin_crypto}-{destination_crypto}",
            )

        return {
            "monto": final_amount,
            "moneda_destino": destination_crypto,
            "moneda_intermediaria": intermediary,
        }
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing conversion: {str(e)}"
        )


async def call_external_api(url: str, params: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, "response") else 500
            raise HTTPException(
                status_code=status_code, detail=f"External API error: {str(e)}"
            )


async def get_all_tickers():
    url = "https://www.buda.com/api/v2/tickers"
    return await call_external_api(url)


async def get_most_destination_crypto_from_amount(
    origin_crypto: str, destination_crypto: str, amount: float
):
    tickers = await get_all_tickers()
    # We store the tickers in a dictionary for O(1) lookup time.
    tickers_dict = {}

    market_id = f"{origin_crypto}-{destination_crypto}"
    inverse_market_id = f"{destination_crypto}-{origin_crypto}"

    for ticker in tickers["tickers"]:
        # Does the direct market exist?
        if ticker["market_id"] == market_id:
            to_amount = calculate_to_amount_from_ticker(
                ticker["last_price"], amount, origin_crypto, destination_crypto
            )
            return to_amount, None
        # Does the inverse market exist?
        if ticker["market_id"] == inverse_market_id:
            to_amount = calculate_to_amount_from_ticker(
                ticker["last_price"], amount, origin_crypto, destination_crypto
            )
            return to_amount, None
        # Store tickers in a dictionary for O(1) lookup time.
        tickers_dict[ticker["market_id"]] = ticker["last_price"]

    best_rate = None
    best_intermediary = None

    for market_id, last_price in tickers_dict.items():
        # Split the market_id to get the currencies
        first, second = market_id.split("-")
        intermediary = None

        # We need to see if the from currency is part of the market_id.
        if first == origin_crypto:
            intermediary = second
        elif second == origin_crypto:
            intermediary = first
        else:
            continue

        # Calculate the amount of the intermediary currency from the from_amount.
        intermediary_amount = calculate_to_amount_from_ticker(
            last_price, amount, intermediary
        )

        # We need to see if the intermediary currency and the destination_crypto have a market_id.
        final_market_id = f"{intermediary}-{destination_crypto}"
        inverse_final_market_id = f"{destination_crypto}-{intermediary}"
        if final_market_id in tickers_dict:
            possible_rate = calculate_to_amount_from_ticker(
                tickers_dict[final_market_id], intermediary_amount, destination_crypto
            )
        elif inverse_final_market_id in tickers_dict:
            possible_rate = calculate_to_amount_from_ticker(
                tickers_dict[inverse_final_market_id],
                intermediary_amount,
                destination_crypto,
            )
        else:
            continue

        # We update the final_amount if its better than the current best_rate.
        # And update the best intermediary
        if best_rate is None or possible_rate > best_rate:
            best_rate = possible_rate
            best_intermediary = intermediary

    return best_rate, best_intermediary


# In this function we expect the last_price to be of ticker of market_id origin_crypto-destination_crypto or destination_crypto-origin_crypto.
def calculate_to_amount_from_ticker(
    last_price: list, from_amount: float, destination_crypto: str
):
    price = last_price[0]
    crypto = last_price[1]
    if crypto == destination_crypto:
        return float(price) * from_amount
    else:
        return from_amount / float(price)
