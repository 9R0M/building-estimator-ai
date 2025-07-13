#service/nearest
import geopandas as gpd
import os
import json
import logging
from typing import Dict, Any
from geopy.distance import geodesic
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/land_price")
def load_geojson(path: str) -> gpd.GeoDataFrame:
   if not os.path.exists(path):
       logger.debug(f"ファイル未検出: {path}")
       raise FileNotFoundError(path)
   try:
       gdf = gpd.read_file(path)
       logger.info(f"GeoJSON 読込成功: {os.path.basename(path)}, 件数={len(gdf)}")
       return gdf
   except Exception:
       logger.exception(f"GeoJSON 読込失敗: {path}")
       raise
def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   path = os.path.join(DATA_DIR, f"{pref_code}_current.geojson")
   return load_geojson(path)
def load_old_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   path = os.path.join(DATA_DIR, f"{pref_code}_old.geojson")
   return load_geojson(path)
def find_nearest_land_price(
   gdf: gpd.GeoDataFrame,
   lat: float,
   lon: float
) -> Dict[str, Any]:
   if gdf.empty:
       logger.error("GeoDataFrame が空です")
       raise ValueError("データが存在しません")
   target = (lat, lon)
   try:
       # 空間インデックス利用と検索性能向上（max_distanceなども有効）()
       df = gdf.copy()
       df["distance"] = df.geometry.apply(lambda geom: geodesic((geom.y, geom.x), target).meters)
   except Exception:
       logger.exception("距離計算エラー")
       raise RuntimeError("距離算出に失敗しました")
   nearest = df.loc[df["distance"].idxmin()]
   logger.info(f"Nearest record found: distance={nearest.distance:.1f}m")
   year = _safe_int(nearest.get("L01_002"))
   price = _safe_float(nearest.get("L01_006"))
   use = nearest.get("L01_003")
   rec = nearest.drop(labels=["geometry"]).to_dict()
   full_json = json.dumps(rec, default=str, ensure_ascii=False)
   logger.debug(f"Nearest full record: {full_json}")
   return {
       "record": nearest,
       "distance": nearest.distance,
       "year": year,
       "price": price,
       "use": use,
       "full_record_json": full_json,
   }
def _safe_int(val: Any) -> Any:
   try:
       return int(val) if val is not None else None
   except Exception:
       logger.warning(f"整数変換失敗: {val}")
       return None
def _safe_float(val: Any) -> Any:
   try:
       return float(val) if val is not None else None
   except Exception:
       logger.warning(f"浮動小数点変換失敗: {val}")
       return None