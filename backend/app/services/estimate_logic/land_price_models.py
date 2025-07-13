# backend/app/routers/land_price.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import geopandas as gpd
import pandas as pd
import logging
from functools import lru_cache
from shapely.geometry import Point
from geopy.distance import geodesic
router = APIRouter(
   prefix="/land-price",
   tags=["land-price"]
)
logger = logging.getLogger(__name__)
class LandPriceResponse(BaseModel):
   location: str
   price: float
   use: Optional[str]
   year: Optional[int]
   distance_m: float
@router.get("/", response_model=LandPriceResponse, summary="Get nearest land price data")
async def get_land_price(
   lat: float = Query(..., description="Latitude, e.g. 35.66"),
   lon: float = Query(..., description="Longitude, e.g. 139.70"),
   pref_code: str = Query(..., description="Prefecture code, e.g. '13'")
):

   """
   指定された緯度・経度・都道府県コードから、
   最寄りの地価データを返します。
   """
   try:
       gdf = load_land_price_data(pref_code)
   except FileNotFoundError as e:
       logger.warning(f"No data for pref_code={pref_code}: {e}")
       raise HTTPException(status_code=404, detail=str(e))
   target = (lat, lon)
   gdf2 = gdf.assign(
       distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), target).meters)
   )
   nearest = gdf2.loc[gdf2["distance"].idxmin()]
   return LandPriceResponse(
       location=nearest.get("L01_001", ""),
       price=float(nearest.get("L01_006", 0)),
       use=nearest.get("L01_003"),
       year=nearest.get("L01_002"),
       distance_m=round(nearest["distance"], 1)
   )

def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:

    df = pd.DataFrame({

        "location": ["デモ地点"],

        "price": [300000],

        "geometry": [Point(139.7300, 35.6100)]

    })

    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
 