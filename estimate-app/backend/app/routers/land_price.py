# backend/app/routers/land_price.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from geopy.distance import geodesic
import logging

# === app/routers/land_price.py ===
from app.models.land_price_dto import LandPriceDTO
from app.services.logic.land_price_service import ILandPriceRepository
from app.services.logic.land_price_models import load_land_price_data


router = APIRouter(
    prefix="/land-price",
    tags=["land-price"]
)

logger = logging.getLogger(__name__)

@router.get("/", response_model=LandPriceDTO, summary="Get nearest land price")

# TODO: 関数の特に返り値を修正する
async def get_land_price(
    lat: float = Query(..., description="Latitude (例: 35.66)"),
    lon: float = Query(..., description="Longitude (例: 139.70)"),
    pref_code: str = Query(..., description="Prefecture code (例: '13')")
):

    """
    緯度・経度・都道府県コードに基づいて最寄りの地価情報を返す。
    """

    try:
        gdf = load_land_price_data(pref_code)

    except FileNotFoundError as e:
        logger.warning(f"No data for pref_code={pref_code}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    target = (lat, lon)

    df = gdf.assign(
        distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), target).meters)
    )

    nearest = df.loc[df["distance"].idxmin()]

    return LandPriceDTO(
        location="",
        price=float(0),
        distance_m=0.0
    )
