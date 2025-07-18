# backend/app/routers/__init__.py
from fastapi import FastAPI
from . import land_price, estimate  # 他のルーターが増えたらここに追記
def register_routers(app: FastAPI):
   """
   すべてのルーターをFastAPIアプリに登録する。
   """
   app.include_router(land_price.router)
   app.include_router(estimate.router)