# backend/app/services/logic/estimate_logic.py
unit_prices = {
    "RC": 250000,     # 円/㎡
    "SRC": 300000,
    "S": 200000
}
region_factors = {
   "北海道": 1.05,
   "青森県": 0.95,
   "岩手県": 0.95,
   "宮城県": 1.00,
   "秋田県": 0.94,
   "山形県": 0.95,
   "福島県": 0.97,
   "茨城県": 1.00,
   "栃木県": 0.99,
   "群馬県": 0.98,
   "埼玉県": 1.08,
   "千葉県": 1.08,
   "東京都": 1.20,
   "神奈川県": 1.15,
   "新潟県": 0.96,
   "富山県": 0.97,
   "石川県": 0.98,
   "福井県": 0.96,
   "山梨県": 0.98,
   "長野県": 0.97,
   "岐阜県": 0.98,
   "静岡県": 1.02,
   "愛知県": 1.10,
   "三重県": 0.98,
   "滋賀県": 0.99,
   "京都府": 1.05,
   "大阪府": 1.15,
   "兵庫県": 1.08,
   "奈良県": 0.97,
   "和歌山県": 0.96,
   "鳥取県": 0.94,
   "島根県": 0.94,
   "岡山県": 0.98,
   "広島県": 1.00,
   "山口県": 0.97,
   "徳島県": 0.95,
   "香川県": 0.96,
   "愛媛県": 0.96,
   "高知県": 0.95,
   "福岡県": 1.05,
   "佐賀県": 0.94,
   "長崎県": 0.95,
   "熊本県": 0.96,
   "大分県": 0.96,
   "宮崎県": 0.94,
   "鹿児島県": 0.95,
   "沖縄県": 1.10,
   "その他": 1.00  # 地名が不明な場合の補正
}
# 用途別係数
unit_prices = {
   "RC": 250_000,
   "SRC": 300_000,
   "S": 200_000,
   "木造": 150_000,
}
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
   floor_factor = get_floor_factor(floors)
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
   region_factor = region_factors.get(region, 1.0)
   total_factor = usage_factor * floor_factor * age_factor * region_factor
   total_cost = area * unit_price * total_factor
   return round(total_cost, 0)

def get_floor_factor(floors: int, *, beyond_top_increment: float = 0.01) -> float:
   """
   階数係数（1〜50階はテーブル値を数式で完全再現、51階以上は逓増）
   - 1階: 1.00
   - 2階: 1.02
   - 3〜10階: 1.00 + 0.01*階
   - 11〜15階: 1.10 + 0.02*(階-10)
   - 16〜25階: 1.20 + 0.02*(階-15)
   - 26〜50階: 1.40 + 0.03*(階-25)
   - 51階以上: 2.15 + beyond_top_increment*(階-50)
   """

   if floors <= 1:
       return 1.00
   if floors == 2:
       return 1.02
   if 3 <= floors <= 10:
       return 1.00 + 0.01 * floors
   if 11 <= floors <= 15:
       return 1.10 + 0.02 * (floors - 10)
   if 16 <= floors <= 25:
       return 1.20 + 0.02 * (floors - 15)
   if 26 <= floors <= 50:
       return 1.40 + 0.03 * (floors - 25)
   # 51階以上
   return 2.15 + beyond_top_increment * (floors - 50)
   
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