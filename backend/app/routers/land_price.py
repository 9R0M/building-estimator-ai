# backend/app/routers/land_price.py

from fastapi import APIRouter, HTTPException, Query

from pydantic import BaseModel

from typing import Optional

import logging

from app.services.estimate_logic.land_price_models import load_land_price_data

router = APIRouter(

    prefix="/land-price",

    tags=["land-price"]

)

logger = logging.getLogger(__name__)

class LandPriceResponse(BaseModel):

    location: str = ""

    price: float = 0.0

    use: Optional[str] = None

    year: Optional[int] = None

    distance_m: float

@router.get("/", response_model=LandPriceResponse, summary="Get nearest land price")

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

    return LandPriceResponse(

        location=nearest.get("L01_001", ""),

        price=float(nearest.get("L01_006", 0)),

        use=nearest.get("L01_003"),

        year=int(nearest.get("L01_002")) if nearest.get("L01_002") else None,

        distance_m=round(nearest["distance"], 1)

    )
