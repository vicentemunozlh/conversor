from fastapi import APIRouter, HTTPException, Query
from app.api.services.buda import get_most_destination_currency_from_amount
from enum import Enum
import httpx

router = APIRouter()


class Currency(str, Enum):
    CLP = "CLP"
    PEN = "PEN"
    COP = "COP"


@router.get(
    "/",
    summary="API Status",
    description="Retorna el estado actual de la API e información básica",
    responses={
        200: {
            "description": "API is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "version": "0.0.1",
                        "service": "Currency Conversion API",
                        "endpoints": {"status": "/", "conversion": "/best-conversion"},
                    }
                }
            },
        }
    },
)
async def get_status():
    return {
        "status": "ok",
        "version": "0.0.1",
        "service": "Currency Conversion API",
        "endpoints": {"status": "/", "conversion": "/best-conversion"},
    }


@router.get(
    "/best-conversion",
    summary="Obtener la mejor tasa de conversión entre monedas",
    description="""
    Convierte entre las monedas CLP, PEN y COP usando la conversion con 1 criptomoneda intermediaria.
    
    **IMPORTANTE**: Las monedas deben ser ingresadas en MAYÚSCULAS (CLP, PEN, COP).
    """,
    responses={
        200: {
            "description": "Successful conversion",
            "content": {
                "application/json": {
                    "example": {
                        "monto": 2.5,
                        "moneda_destino": "PEN",
                        "moneda_intermediaria": "BTC",
                    }
                }
            },
        },
        404: {
            "description": "No conversion path found",
            "content": {
                "application/json": {
                    "example": {"detail": "No conversion path found for CLP-PEN"}
                }
            },
        },
        503: {
            "description": "External service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service temporarily unavailable. Please try again later."
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred. Please try again later."
                    }
                }
            },
        },
    },
)
async def best_conversion(
    origin_currency: Currency = Query(
        ..., description="Moneda de origen (debe ser CLP, PEN o COP en MAYÚSCULAS)"
    ),
    destination_currency: Currency = Query(
        ..., description="Moneda de destino (debe ser CLP, PEN o COP en MAYÚSCULAS)"
    ),
    amount: float = Query(
        ...,
        description="Monto a convertir de la moneda de origen",
        gt=0,  # greater than 0
    ),
):
    try:
        final_amount, intermediary = await get_most_destination_currency_from_amount(
            origin_currency, destination_currency, amount
        )
        if final_amount is None:
            raise HTTPException(
                status_code=404,
                detail=f"No conversion path found for {origin_currency}-{destination_currency}",
            )

        return {
            "monto": final_amount,
            "moneda_destino": destination_currency,
            "moneda_intermediaria": intermediary,
        }
    # We re-raise the HTTPException from no conversion path found.
    except HTTPException:
        raise
    except httpx.HTTPError:
        # External service errors
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail="Service temporarily unavailable. Please try again later.",
        )
    except Exception:
        # Truly unexpected errors
        raise HTTPException(
            status_code=500,  # Internal Server Error
            detail="An unexpected error occurred. Please try again later.",
        )
