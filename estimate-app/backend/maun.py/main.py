#backend/main.py,
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil

from typing import Dict, Any  # ← 差し込み！

from estimate_logic import extract_building_info_enhanced

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=[""],
)

@app.post("/extract-info/")
async def extract_info(file: UploadFile = File(...)) -> Dict[str, Any]:
    temp_path = "temp.jpg"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_building_info_enhanced(temp_path)
    return {"result": result}



