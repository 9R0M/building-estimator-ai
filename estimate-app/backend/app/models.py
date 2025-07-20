# app/models.py
from pydantic import BaseModel
class EstimateRequest(BaseModel):
   base_unit_cost: float
   structure: str
   area: float
   usage: str
   region: str
   floors: int
   building_age: int