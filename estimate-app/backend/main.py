from fastapi import FastAPI
from pydantic import BaseModel
from estimate_logic import estimate_cost

app = FastAPI()

class EstimateInput(BaseModel):
    structure: str
    floors: int
    area: float
    usage: str

@app.post("/estimate")
def get_estimate(data: EstimateInput):
    result = estimate_cost(data.structure, data.floors, data.area, data.usage)
    return {"estimate": result}