from fastapi import APIRouter, HTTPException, Query
from app.api.services.buda import get_most_destination_crypto_from_amount
from enum import Enum

router = APIRouter()


class Currency(str, Enum):
    CLP = "CLP"
    PEN = "PEN"
    COP = "COP"


@router.get(
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
