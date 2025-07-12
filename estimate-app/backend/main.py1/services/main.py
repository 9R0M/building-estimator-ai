import sys
import os
import logging
# logsフォルダ作成（なければ）
os.makedirs("logs", exist_ok=True)
# sys.path設定
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
# ログ設定
logging.basicConfig(
   level=logging.INFO,
   format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
   handlers=[
       logging.StreamHandler(sys.stdout),
       logging.FileHandler("logs/app.log", encoding="utf-8")
   ]
)
from fastapi import FastAPI, Request, UploadFile, File, APIRouter
from services.extract_info import extract_info_from_blueprint
from services.land_price_models import router as land_price_router
from app.estimate_logic import estimate_cost
from app.models import EstimateRequest
from services.land_price_models import load_land_price_data, find_nearest_land_price
# FastAPI本体
from services.aut_estimate import router as auto_estimate_router
app = FastAPI()
app.include_router(auto_estimate_router)

# アクセスログミドルウェア
@app.middleware("http")
async def log_requests(request: Request, call_next):
   ip = request.client.host if request.client else "unknown"
   path = request.url.path
   query_params = dict(request.query_params)
   logging.getLogger("api_logger").info(
       f"[アクセス] IP={ip} PATH={path} PARAMS={query_params}"
   )
   response = await call_next(request)
   return response
# ルーター設定
router = APIRouter()
@router.post("/extract-info/")
async def extract_info(file: UploadFile = File(...)):
   result = extract_info_from_blueprint(file)
   return result
# ルーター登録
app.include_router(router)
app.include_router(land_price_router)
# 推定ルート
@app.post("/estimate-with-location/")
def estimate_with_location(req: EstimateRequest, lat: float, lon: float, pref_code: str):
   try:
       gdf = load_land_price_data(pref_code)
       nearest = find_nearest_land_price(gdf, lat, lon)
       region = nearest["location"]
   except Exception:
       region = req.region if req.region else "その他"
   cost = estimate_cost(
       req.structure,
       req.area,
       req.usage,
       region,
       req.floors,
       req.building_age,
   )
   return {"estimated_cost": cost, "region": region}