from fastapi import APIRouter
from app.api.v1.endpoints import population, livability, statistics, prediction, auth

api_router = APIRouter()

# 各エンドポイントルーターを登録
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(population.router, prefix="/population", tags=["population"])
api_router.include_router(livability.router, prefix="/livability", tags=["livability"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(prediction.router, tags=["prediction"])