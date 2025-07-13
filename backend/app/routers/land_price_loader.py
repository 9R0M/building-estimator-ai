# backend/app/routers/land_price.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import logging
from geopy.distance import geodesic
from app.services.land_price_models import (
   load_land_price_data,  # 現行年度データ取得
   load_old_land_price_data,  # 過去年度データ取得用（仮想）
)
router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)
class LandPriceResponse(BaseModel):
   location: str
   price: float
   use: Optional[str]
   year: Optional[int]
   distance_m: float
   source: str  # "current" または "old"
@router.get("/", response_model=LandPriceResponse, summary="Get nearest land price")
async def get_land_price(
   lat: float = Query(..., ge=-90, le=90, description="緯度（-90〜90）"),
   lon: float = Query(..., ge=-180, le=180, description="経度（-180〜180）"),
   pref_code: str = Query(..., regex=r"^\d{2}$", description="都道府県コード（2桁）")
):
   logger.info(f"地価取得リクエスト: lat={lat}, lon={lon}, pref_code={pref_code}")
   # --- Step1: 現行年度データ読み込み ---
   try:
       gdf = load_land_price_data(pref_code)
       if gdf.empty:
           raise HTTPException(status_code=404, detail="現行年度の地価データが存在しません")
       source = "current"
   except FileNotFoundError:
       logger.warning("現行年度データなし → 過去年度から取得試行")
       # --- OLD対応: 過去年度データ読み込み ---
       try:
           gdf = load_old_land_price_data(pref_code)
           if gdf.empty:
               raise HTTPException(status_code=404, detail="過去年度含め地価データが見つかりません")
           source = "old"
       except FileNotFoundError:
           logger.error("地価データが一切存在しません")
           raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except HTTPException:
           raise
       except Exception as e:
           logger.exception("過去年度地価データの読み込み中にエラー")
           raise HTTPException(status_code=500, detail="過去年度地価データの読み込みに失敗しました")
   except HTTPException:
       raise
   except Exception:
       logger.exception("現行年度地価データの読み込み中にエラー")
       raise HTTPException(status_code=500, detail="地価データの読み込みに失敗しました")
   # --- Step2: 最近傍検索 ---
   try:
       df = gdf.assign(
           distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), (lat, lon)).meters)
       )
       nearest = df.loc[df.distance.idxmin()]
   except Exception:
       logger.exception("最近傍地価の算出中にエラー")
       raise HTTPException(status_code=500, detail="地価データの解析に失敗しました")
   # --- Step3: レスポンス整形 ---
   year_val = nearest.get("L01_002")
   try:
       year = int(year_val) if year_val is not None else None
   except Exception:
       logger.warning(f"年度の変換に失敗: {year_val}")
       year = None
   return LandPriceResponse(
       location=nearest.get("L01_001", ""),
       price=float(nearest.get("L01_006", 0)),
       use=nearest.get("L01_003"),
       year=year,
       distance_m=round(nearest.distance, 1),
       source=source,
   )


    df = pd.DataFrame({

        "location": ["デモ地点"],

        "price": [300000],

        "geometry": [Point(139.7300, 35.6100)]

    })

    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")