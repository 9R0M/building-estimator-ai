#routers/estimate.py
from fastapi import APIRouter, HTTPException
import logging
from geopy.distance import geodesic
from app.models.estimate_models import EstimateRequest, EstimateResponse
from app.services.logic.land_price_models import load_land_price_data
from app.services.logic.estimate_logic import estimate_cost
router = APIRouter(prefix="/estimate", tags=["estimate"])
logger = logging.getLogger("estimate")
@router.post("/", response_model=EstimateResponse)
async def perfome_estimate(req: EstimateRequest):
   logger.info(f"Request: {req.json()}")
   try:
       gdf = load_land_price_data(req.pref_code)
   except FileNotFoundError as e:
       raise HTTPException(status_code=404, detail=str(e))
   if gdf.empty:
       raise HTTPException(status_code=404, detail="地価データが存在しません")
   try:
       df = gdf.assign(distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), (req.lat, req.lon)).meters))
       nearest = df.loc[df['distance'].idxmin()]
   except Exception:
       raise HTTPException(status_code=500, detail="地価距離計算に失敗しました")
   region = str(nearest.get("L01_001") or "")
   cost = estimate_cost(req.structure, req.area, req.usage, region, req.floors, req.building_age)
   return EstimateResponse(estimated_amount=cost, breakdown={}, land_price=None)