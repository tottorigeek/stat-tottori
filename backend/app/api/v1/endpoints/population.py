from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.population import PopulationResponse, PopulationSummary
from app.services.population_service import PopulationService

router = APIRouter()
population_service = PopulationService()


@router.get("/", response_model=List[PopulationResponse])
async def get_population_data(
    prefecture_code: str = "31",  # 鳥取県
    municipality_code: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """人口データを取得する"""
    try:
        data = await population_service.get_population_data(
            db=db,
            prefecture_code=prefecture_code,
            municipality_code=municipality_code,
            year_start=year_start,
            year_end=year_end
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=PopulationSummary)
async def get_population_summary(
    prefecture_code: str = "31",
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """人口サマリーデータを取得する"""
    try:
        summary = await population_service.get_population_summary(
            db=db,
            prefecture_code=prefecture_code,
            year=year
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend")
async def get_population_trend(
    prefecture_code: str = "31",
    years: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """人口推移データを取得する（Chart.js用フォーマット）"""
    try:
        trend_data = await population_service.get_population_trend_chart_data(
            db=db,
            prefecture_code=prefecture_code,
            years=years
        )
        return {
            "labels": trend_data["years"],
            "datasets": [
                {
                    "label": "総人口",
                    "data": trend_data["total_population"],
                    "borderColor": "rgb(59, 130, 246)",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "tension": 0.4
                },
                {
                    "label": "生産年齢人口",
                    "data": trend_data["working_age_population"],
                    "borderColor": "rgb(34, 197, 94)",
                    "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    "tension": 0.4
                },
                {
                    "label": "老年人口",
                    "data": trend_data["elderly_population"],
                    "borderColor": "rgb(239, 68, 68)",
                    "backgroundColor": "rgba(239, 68, 68, 0.1)",
                    "tension": 0.4
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_population_forecast(
    prefecture_code: str = "31",
    municipality_code: Optional[str] = None,
    years_ahead: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """人口予測データを取得する"""
    try:
        forecast_data = await population_service.get_population_forecast(
            db=db,
            prefecture_code=prefecture_code,
            municipality_code=municipality_code,
            years_ahead=years_ahead
        )
        return forecast_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))