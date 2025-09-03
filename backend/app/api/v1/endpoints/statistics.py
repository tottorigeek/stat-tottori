from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.statistics_service import StatisticsService

router = APIRouter()
statistics_service = StatisticsService()


@router.get("/kpi-dashboard")
async def get_kpi_dashboard_data(
    prefecture_code: str = "31",
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """KPIダッシュボード用データを取得する"""
    try:
        kpi_data = await statistics_service.get_kpi_dashboard_data(
            db=db,
            prefecture_code=prefecture_code,
            year=year
        )
        return kpi_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation-matrix")
async def get_correlation_matrix(
    indicators: List[str] = Query(...),
    prefecture_code: str = "31",
    years: int = Query(default=10, ge=5, le=30),
    db: Session = Depends(get_db)
):
    """指標間相関関係マトリクスを取得する"""
    try:
        correlation_data = await statistics_service.get_correlation_matrix(
            db=db,
            indicators=indicators,
            prefecture_code=prefecture_code,
            years=years
        )
        return correlation_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/time-series-analysis")
async def get_time_series_analysis(
    indicator: str,
    prefecture_code: str = "31",
    municipality_code: Optional[str] = None,
    years: int = Query(default=20, ge=10, le=50),
    include_forecast: bool = False,
    db: Session = Depends(get_db)
):
    """時系列分析データを取得する"""
    try:
        analysis_data = await statistics_service.get_time_series_analysis(
            db=db,
            indicator=indicator,
            prefecture_code=prefecture_code,
            municipality_code=municipality_code,
            years=years,
            include_forecast=include_forecast
        )
        return analysis_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparative-analysis")
async def get_comparative_analysis(
    base_municipality: str,
    comparison_municipalities: List[str] = Query(...),
    indicators: List[str] = Query(...),
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """地域間比較分析データを取得する"""
    try:
        comparison_data = await statistics_service.get_comparative_analysis(
            db=db,
            base_municipality=base_municipality,
            comparison_municipalities=comparison_municipalities,
            indicators=indicators,
            year=year
        )
        return comparison_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geographic-data")
async def get_geographic_data(
    indicator: str,
    prefecture_code: str = "31",
    year: Optional[int] = None,
    format: str = "geojson",
    db: Session = Depends(get_db)
):
    """地図表示用地理データを取得する（Mapbox GL用）"""
    try:
        geo_data = await statistics_service.get_geographic_data(
            db=db,
            indicator=indicator,
            prefecture_code=prefecture_code,
            year=year,
            output_format=format
        )
        return geo_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))