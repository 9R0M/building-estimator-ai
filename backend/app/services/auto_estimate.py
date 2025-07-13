from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from app.services.extract_info import extract_info_from_blueprint
from app.services.land_price_models import load_land_price_data
from app.estimate_logic import estimate_cost

router = APIRouter()
@router.post("/auto-estimate/")
async def auto_estimate(
   file: UploadFile = File(...),
   lat: float = Query(...),
   lon: float = Query(...),
   pref_code: str = Query(...),
   usage: str = Query(...),
   building_age: int = Query(10)
):
   # Step 1: 図面画像 → 構造・階数・面積の抽出
   try:
       extracted = extract_info_from_blueprint(file)
       structure = extracted.get("structure", "RC")
       floors = extracted.get("floors", 1)
       area = extracted.get("area", 100.0)
   except Exception as e:
       raise HTTPException(status_code=400, detail=f"図面解析に失敗しました: {str(e)}")
   # Step 2: 緯度経度・都道府県コード → 最寄りの地価データ取得
   try:
       gdf = load_land_price_data(pref_code)
       nearest = find_nearest_land_price(gdf, lat, lon)
       region = nearest.get("location", "その他")
   except Exception as e:
       region = "その他"  # 地価失敗時もfallback
       nearest = None
   # Step 3: AIによる建設費推定
   try:
       estimated_cost = estimate_cost(
           structure=structure,
           area=area,
           usage=usage,
           region=region,
           floors=floors,
           building_age=building_age,
       )
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"推定処理に失敗しました: {str(e)}")
   return {
       "estimated_cost": estimated_cost,
       "structure": structure,
       "floors": floors,
       "area": area,
       "region": region,
       "usage": usage,
       "building_age": building_age,
       "land_price_info": nearest
   }