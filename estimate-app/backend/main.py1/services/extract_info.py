# services/extract_info.py
import pytesseract
import cv2
import numpy as np
import os
from fastapi import UploadFile
from typing import Dict
def extract_info_from_blueprint(file: UploadFile) -> Dict[str, str]:
   contents = file.file.read()
   nparr = np.frombuffer(contents, np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   text = pytesseract.image_to_string(img, lang='jpn+eng')
   structure = "不明"
   floors = "不明"
   area = "不明"
   # 簡易ルールベース判定（仮）
   if "RC" in text or "鉄筋" in text:
       structure = "RC"
   elif "S造" in text:
       structure = "S"
   elif "木造" in text:
       structure = "木造"
   import re
   floors_match = re.search(r"[地上|地下]?(\d+)階", text)
   if floors_match:
       floors = floors_match.group(1)
   area_match = re.search(r"(\d{2,4}\.?[\d]*)[㎡m²]", text)
   if area_match:
       area = area_match.group(1)
   return {
       "structure": structure,
       "floors": floors,
       "area": area
   }