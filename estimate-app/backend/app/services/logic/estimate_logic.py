# backend/app/services/logic/estimate_logic.py
unit_prices = {
    "RC": 250000,     # 円/㎡
    "SRC": 300000,
    "S": 200000
}
region_factors = {
   "北海道": 1.05,
   "青森": 0.95,
   "岩手": 0.95,
   "宮城": 1.00,
   "秋田": 0.94,
   "山形": 0.95,
   "福島": 0.97,
   "茨城": 1.00,
   "栃木": 0.99,
   "群馬": 0.98,
   "埼玉": 1.08,
   "千葉": 1.08,
   "東京": 1.20,
   "神奈川": 1.15,
   "新潟": 0.96,
   "富山": 0.97,
   "石川": 0.98,
   "福井": 0.96,
   "山梨": 0.98,
   "長野": 0.97,
   "岐阜": 0.98,
   "静岡": 1.02,
   "愛知": 1.10,
   "三重": 0.98,
   "滋賀": 0.99,
   "京都": 1.05,
   "大阪": 1.15,
   "兵庫": 1.08,
   "奈良": 0.97,
   "和歌山": 0.96,
   "鳥取": 0.94,
   "島根": 0.94,
   "岡山": 0.98,
   "広島": 1.00,
   "山口": 0.97,
   "徳島": 0.95,
   "香川": 0.96,
   "愛媛": 0.96,
   "高知": 0.95,
   "福岡": 1.05,
   "佐賀": 0.94,
   "長崎": 0.95,
   "熊本": 0.96,
   "大分": 0.96,
   "宮崎": 0.94,
   "鹿児島": 0.95,
   "沖縄": 1.10,
   "その他": 1.00  # 地名が不明な場合の補正
}
# 用途別係数
usage_factors = {
   "住宅": 1.0,
   "オフィス": 1.1,
   "商業施設": 1.2,
   "工場": 1.15
}
def estimate_cost(structure, area, usage, region, floors, building_age):
   unit_price = unit_prices.get(structure.upper(), 220000)
   usage_factor = usage_factors.get(usage, 1.0)
   # 階数補正
   if floors >= 10:
       floor_factor = 1.1
   elif floors >= 5:
       floor_factor = 1.05
   else:
       floor_factor = 1.0
   # 築年数補正
   if building_age >= 30:
       age_factor = 1.15
   elif building_age >= 20:
       age_factor = 1.10
   elif building_age >= 10:
       age_factor = 1.05
   else:
       age_factor = 1.0
   # 地域係数（region は今は使わないが、今後の拡張のため保持）
   region_factor = 1.0  # 仮
   total_factor = usage_factor * floor_factor * age_factor * region_factor
   total_cost = area * unit_price * total_factor
   return round(total_cost, 0)
   
import cv2
import pytesseract
import re
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
# === app/services/logic/estimate_logic.py ===
from app.models.estimate_models import EstimateRequest, EstimateResponse
from app.models.land_price_dto import LandPriceDTO
from app.services.logic.land_price_service import ILandPriceRepository
from app.services.storage.history_repo import IHistoryRepository
from app.models.history_models import HistoryRecord

def extract_building_info_enhanced(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from path: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='eng')
    structure = "RC" if "RC" in text else "不明"
    floor_match = re.search(r"Floors\s[:-]?\s(\d+)", text, re.IGNORECASE)
    floors = int(floor_match.group(1)) if floor_match else 1
    area_match = re.search(r"Total\s+Area\s[:-]?\s(\d+[,.]?\d*)\s*(sqm|m2)?", text, re.IGNORECASE)
    area = float(area_match.group(1).replace(',', '')) if area_match else 100.0
    return {
        "structure": structure,
        "floors": floors,
        "area": area,
        "raw_text": text
    }

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],  # ←Viteのポート
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/extract-info/")
async def extract_info(file: UploadFile = File(...)):
    temp_path = "temp.jpg"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = extract_building_info_enhanced(temp_path)
    return result

# TODO: 関数実装をする
class EstimateService():
    def __init__(self, lp_repo: ILandPriceRepository, history_repo: IHistoryRepository) -> None:
        pass

    def estimate(self, req: EstimateRequest) -> EstimateResponse:
        return EstimateResponse(
            estimated_amount=0.0,
            breakdown={},
            land_price=None
        )