import os
import pandas as pd
import geopandas as gpd
import logging

logger = logging.getLogger(__name__)
 
from shapely.geometry import Point

from geopy.distance import geodesic

from functools import lru_cache

from fastapi import APIRouter, HTTPException, Query
import logging
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geopy.distance import geodesic
from functools import lru_cache

BASE_DIR = "data/L01-23_GML"

@lru_cache()

def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:

   files = sorted([
       f for f in os.listdir(BASE_DIR)
       if f.startswith(f"L01-23_{pref_code}_") and f.endswith(".gml")
   ])

   if not files:
       available_files = os.listdir(BASE_DIR)
       logger.warning(
           f"[地価データ読み込み失敗] pref_code='{pref_code}' に該当する GML ファイルが見つかりません。"
           f"対象ディレクトリ: {BASE_DIR}, ファイル一覧: {available_files}"
       )
       raise FileNotFoundError(
           f"GMLファイルが見つかりません: 指定コード={pref_code} / フォルダ内ファイル数={len(available_files)}"
       )

   # Load and concatenate all matching GML files into a single GeoDataFrame
   gdfs = [gpd.read_file(os.path.join(BASE_DIR, f)) for f in files]
   gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True)) if len(gdfs) > 1 else gdfs[0]
   return gdf

def find_nearest_land_price(gdf: gpd.GeoDataFrame, lat: float, lon: float) -> dict:

    target = (lat, lon)

    gdf["distance"] = gdf.geometry.apply(lambda x: geodesic((x.y, x.x), target).meters)

    nearest = gdf.sort_values("distance").iloc[0]

    return {

        "location": nearest["L01_001"],

        "price": nearest["L01_006"],

        "use": nearest["L01_003"],

        "year": nearest["L01_002"],

        "distance_m": round(nearest["distance"], 1),

    }
from fastapi import APIRouter, HTTPException, Query
from land_price_loader import load_land_price_data
router = APIRouter()
@router.get("/land-price/")
def get_land_price(
   lat: float = Query(...),
   lon: float = Query(...),
   pref_code: str = Query(...)
):
   try:
       gdf = load_land_price_data(pref_code)
   except FileNotFoundError as e:
       raise HTTPException(status_code=404, detail=str(e))
   result = find_nearest_land_price(gdf, lat, lon)
   return result
   
