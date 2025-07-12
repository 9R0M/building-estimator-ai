unit_prices = {
    "RC": 250000,     # 円/㎡
    "SRC": 300000,
    "S": 200000
}
def estimate_cost(structure, floors, area, usage):
    unit_price = unit_prices.get(structure.upper(), 220000)
    total_cost = area * unit_price
    return round(total_cost)
import cv2
import pytesseract
import re
def extract_building_info_enhanced(image_path: str):
    image = cv2.imread(image_path)
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
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
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