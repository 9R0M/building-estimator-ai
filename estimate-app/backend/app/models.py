# app/models.py
from pydantic import BaseModel
class BuildingInfo(BaseModel):
   structure: str
   usage: str
   floors: int
   building_age: int
   area: float
class LocationInfo(BaseModel):
   lat: float
   lon: float
   pref_code: str  # "13" のような文字列
class EstimateWithLocationRequest(BaseModel):
   building: BuildingInfo
   location: LocationInfo
class EstimateResponse(BaseModel):
   estimated_cost: float
   region: str