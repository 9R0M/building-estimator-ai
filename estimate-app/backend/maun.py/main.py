import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../app')
from fastapi import FastAPI
from app.estimate_logic import estimate_cost
from app.models import EstimateRequest
app = FastAPI()
@app.post("/estimate/")
def estimate(req: EstimateRequest):
   cost = estimate_cost(
       req.base_unit_cost,
       req.area,
       req.usage,
       req.region,
       req.floors,
       req.building_age
   )
   return {"estimated_cost": round(cost)}


