# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
   EstimateWithLocationRequest,
   EstimateResponse,
)
from app.land_price_loader import load_land_price_data
from app.estimate_logic import estimate_cost
from geopy.distance import geodesic
from app.routers import register_routers
import logging
app = FastAPI(

    title="建物見積もりAI API",

    description="地価データと建物構造情報から自動見積もりを行うAPI群",

    version="1.0.0"

)

# CORS ミドルウェア設定
origins = [
   "http://localhost:5173",  # フロントのURL（開発環境の例）
   "http://127.0.0.1:5173",
]
app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,        # "*" は認証付き通信で制限されるため注意  [oai_citation_attribution:0‡Stack Overflow](https://stackoverflow.com/questions/65635346/how-can-i-enable-cors-in-fastapi/66460861?utm_source=chatgpt.com) [oai_citation_attribution:1‡FastAPI](https://fastapi.tiangolo.com/tutorial/cors/?utm_source=chatgpt.com)
   #allow_credentials=True,
   allow_methods=["*"],          # GET, POST, OPTIONS を許可
   allow_headers=["*"],          # Content-Type などを許可
   expose_headers=["*"],
)

# ルーター登録
register_routers(app)
logger = logging.getLogger("estimate_with_location")

@app.post("/estimate-with-location", response_model=EstimateResponse, summary="ネストされた building/location を受け取り見積もりを返す")
async def estimate_with_location(req: EstimateWithLocationRequest):
   logger.info(f"リクエスト受信: {req.json()}")
   # 地価データロード
   try:
       gdf = load_land_price_data(req.location.pref_code)
   except FileNotFoundError as e:
       logger.warning(f"pref_code='{req.location.pref_code}' の地価データが見つかりません: {e}")
       raise HTTPException(status_code=404, detail=str(e))
   if gdf.empty:
       logger.warning("GeoDataFrame が空です")
       raise HTTPException(status_code=404, detail="地価データが存在しません")
   # 距離計算
   target = (req.location.lat, req.location.lon)
   try:
       gdf2 = gdf.assign(
           distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), target).meters)
       )
       nearest = gdf2.loc[gdf2["distance"].idxmin()]
   except Exception as e:
       logger.error(f"最寄地価データの取得に失敗しました: {e}")
       raise HTTPException(status_code=500, detail="最寄地価データの取得に失敗")
   region = str(nearest.get("L01_001") or "不明地域")
   logger.info(f"最寄地域: {region}")
   # 見積り計算
   cost = estimate_cost(
       req.building.structure,
       req.building.area,
       req.building.usage,
       region,
       req.building.floors,
       req.building.building_age,
   )
   logger.info(f"見積結果: {cost}")
   # （オプション）履歴記録などここでDB保存も可能
   return EstimateResponse(estimated_cost=cost, region=region)