# backend/app/routers/estimate.py

from fastapi import APIRouter, HTTPException
from geopy.distance import geodesic
import logging

# === app/routers/estimate.py ===
from app.models.estimate_models import EstimateRequest, EstimateResponse
from app.services.logic.estimate_logic import EstimateService

router = APIRouter(
    prefix="/estimate",
    tags=["estimate"]
)

logger = logging.getLogger("estimate_with_location")

@router.post("/", response_model=EstimateResponse, summary="建物＋位置情報で見積もり計算")

async def perfome_estimate(req: EstimateRequest):
    logger.info(f"リクエスト受信: {req.json()}")

    try:
        gdf = load_land_price_data(req.location.pref_code)

    except FileNotFoundError as e:
        logger.warning(f"pref_code='{req.location.pref_code}' の地価データが見つかりません: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    if gdf.empty:
        raise HTTPException(status_code=404, detail="地価データが存在しません")

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

    cost = estimate_cost(
        req.building.structure,
        req.building.area,
        req.building.usage,
        region,
        req.building.floors,
        req.building.building_age,
    )

    logger.info(f"見積結果: {cost}")

    return EstimateResponse(estimated_cost=cost, region=region)

 