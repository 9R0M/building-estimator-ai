from pydantic import BaseModel
class EstimateRequest(BaseModel):
   structure: str
   floors: int
   area: float
   usage: str