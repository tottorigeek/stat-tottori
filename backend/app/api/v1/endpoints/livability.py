from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.livability import LivabilityScoreResponse, LivabilityComparisonResponse
from app.services.livability_service import LivabilityService

router = APIRouter()
livability_service = LivabilityService()


@router.get("/scores", response_model=List[LivabilityScoreResponse])
async def get_livability_scores(
    prefecture_code: str = "31",
    municipality_code: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """住みやすさスコアを取得する"""
    try:
        scores = await livability_service.get_livability_scores(
            db=db,
            prefecture_code=prefecture_code,
            municipality_code=municipality_code,
            year=year
        )
        return scores
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
async def get_livability_comparison(
    municipality_codes: List[str] = Query(...),
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """複数地域の住みやすさ比較データを取得する"""
    try:
        comparison_data = await livability_service.get_livability_comparison(
            db=db,
            municipality_codes=municipality_codes,
            year=year
        )
        return comparison_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar-chart")
async def get_livability_radar_chart(
    municipality_code: str,
    year: Optional[int] = None,
    user_weights: Optional[str] = None,  # JSON文字列
    db: Session = Depends(get_db)
):
    """住みやすさレーダーチャートデータを取得する（Chart.js用）"""
    try:
        chart_data = await livability_service.get_radar_chart_data(
            db=db,
            municipality_code=municipality_code,
            year=year,
            user_weights=user_weights
        )
        return {
            "labels": [
                "インフラ", "医療・健康", "教育", "環境",
                "経済・雇用", "コミュニティ", "交通", "文化・娯楽"
            ],
            "datasets": [{
                "label": chart_data["municipality_name"],
                "data": chart_data["scores"],
                "borderColor": "rgb(59, 130, 246)",
                "backgroundColor": "rgba(59, 130, 246, 0.2)",
                "pointBackgroundColor": "rgb(59, 130, 246)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgb(59, 130, 246)"
            }]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators")
async def get_livability_indicators(
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """住みやすさ指標マスターデータを取得する"""
    try:
        indicators = await livability_service.get_indicators(
            db=db,
            category=category,
            active_only=active_only
        )
        return indicators
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-score")
async def calculate_custom_livability_score(
    municipality_code: str,
    custom_weights: dict,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """カスタム重み設定で住みやすさスコアを計算する"""
    try:
        custom_score = await livability_service.calculate_custom_score(
            db=db,
            municipality_code=municipality_code,
            custom_weights=custom_weights,
            year=year
        )
        return custom_score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))