# app/routers/__init__.py
from fastapi import FastAPI
from app.routers.estimate import router as estimate_router
from app.routers.extract_info import router as extract_info_router
from app.routers.land_price import router as land_price_router
def register_routers(app: FastAPI):
   app.include_router(estimate_router)
   app.include_router(extract_info_router)
   app.include_router(land_price_router)