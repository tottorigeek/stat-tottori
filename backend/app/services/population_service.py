from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.population import PopulationData, PopulationForecast
from app.schemas.population import PopulationResponse, PopulationSummary
import pandas as pd
from datetime import datetime


class PopulationService:
    """人口データ関連サービス"""

    async def get_population_data(
        self,
        db: Session,
        prefecture_code: str,
        municipality_code: Optional[str] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None
    ) -> List[PopulationResponse]:
        """人口データを取得する"""
        
        query = db.query(PopulationData).filter(
            PopulationData.prefecture_code == prefecture_code
        )
        
        if municipality_code:
            query = query.filter(PopulationData.municipality_code == municipality_code)
        
        if year_start:
            query = query.filter(PopulationData.year >= year_start)
        
        if year_end:
            query = query.filter(PopulationData.year <= year_end)
        
        query = query.order_by(PopulationData.year.desc())
        
        population_data = query.all()
        
        return [PopulationResponse.from_orm(data) for data in population_data]

    async def get_population_summary(
        self,
        db: Session,
        prefecture_code: str,
        year: Optional[int] = None
    ) -> PopulationSummary:
        """人口サマリーを取得する"""
        
        if year is None:
            # 最新年のデータを取得
            latest_year = db.query(func.max(PopulationData.year)).filter(
                PopulationData.prefecture_code == prefecture_code
            ).scalar()
            year = latest_year

        current_data = db.query(PopulationData).filter(
            and_(
                PopulationData.prefecture_code == prefecture_code,
                PopulationData.year == year,
                PopulationData.municipality_code.is_(None)  # 都道府県レベルデータ
            )
        ).first()

        if not current_data:
            raise ValueError(f"指定された年（{year}）のデータが見つかりません")

        # 前年データを取得（変化率計算用）
        previous_data = db.query(PopulationData).filter(
            and_(
                PopulationData.prefecture_code == prefecture_code,
                PopulationData.year == year - 1,
                PopulationData.municipality_code.is_(None)
            )
        ).first()

        # 各種指標を計算
        population_change_rate = None
        if previous_data and previous_data.total_population > 0:
            population_change_rate = (
                (current_data.total_population - previous_data.total_population) / 
                previous_data.total_population * 100
            )

        aging_rate = None
        if current_data.age_65_plus and current_data.total_population > 0:
            aging_rate = current_data.age_65_plus / current_data.total_population * 100

        birth_rate = None
        if current_data.births and current_data.total_population > 0:
            birth_rate = current_data.births / current_data.total_population * 1000

        death_rate = None
        if current_data.deaths and current_data.total_population > 0:
            death_rate = current_data.deaths / current_data.total_population * 1000

        migration_rate = None
        if current_data.net_migration and current_data.total_population > 0:
            migration_rate = current_data.net_migration / current_data.total_population * 1000

        # 年齢階層別構成比
        youth_ratio = None
        working_age_ratio = None
        elderly_ratio = None
        
        if current_data.total_population > 0:
            if current_data.age_0_14:
                youth_ratio = current_data.age_0_14 / current_data.total_population * 100
            if current_data.age_15_64:
                working_age_ratio = current_data.age_15_64 / current_data.total_population * 100
            if current_data.age_65_plus:
                elderly_ratio = current_data.age_65_plus / current_data.total_population * 100

        return PopulationSummary(
            prefecture_code=prefecture_code,
            year=year,
            total_population=current_data.total_population,
            population_change_rate=population_change_rate,
            aging_rate=aging_rate,
            birth_rate=birth_rate,
            death_rate=death_rate,
            migration_rate=migration_rate,
            youth_ratio=youth_ratio,
            working_age_ratio=working_age_ratio,
            elderly_ratio=elderly_ratio
        )

    async def get_population_trend_chart_data(
        self,
        db: Session,
        prefecture_code: str,
        years: int = 10
    ) -> Dict[str, List]:
        """人口推移チャート用データを取得する"""
        
        # 最新年から指定年数分のデータを取得
        latest_year = db.query(func.max(PopulationData.year)).filter(
            PopulationData.prefecture_code == prefecture_code
        ).scalar()

        if not latest_year:
            raise ValueError("データが見つかりません")

        start_year = latest_year - years + 1

        population_data = db.query(PopulationData).filter(
            and_(
                PopulationData.prefecture_code == prefecture_code,
                PopulationData.year >= start_year,
                PopulationData.municipality_code.is_(None)  # 都道府県レベル
            )
        ).order_by(PopulationData.year).all()

        years_list = []
        total_population = []
        working_age_population = []
        elderly_population = []

        for data in population_data:
            years_list.append(str(data.year))
            total_population.append(data.total_population)
            working_age_population.append(data.age_15_64 or 0)
            elderly_population.append(data.age_65_plus or 0)

        return {
            "years": years_list,
            "total_population": total_population,
            "working_age_population": working_age_population,
            "elderly_population": elderly_population
        }

    async def get_population_forecast(
        self,
        db: Session,
        prefecture_code: str,
        municipality_code: Optional[str] = None,
        years_ahead: int = 10
    ) -> List[Dict[str, Any]]:
        """人口予測データを取得する"""
        
        query = db.query(PopulationForecast).filter(
            PopulationForecast.prefecture_code == prefecture_code
        )
        
        if municipality_code:
            query = query.filter(PopulationForecast.municipality_code == municipality_code)
        
        # 指定年数分の予測データを取得
        current_year = datetime.now().year
        end_year = current_year + years_ahead
        
        query = query.filter(
            and_(
                PopulationForecast.target_year >= current_year,
                PopulationForecast.target_year <= end_year
            )
        ).order_by(PopulationForecast.target_year)
        
        forecasts = query.all()
        
        result = []
        for forecast in forecasts:
            result.append({
                "year": forecast.target_year,
                "predicted_population": forecast.predicted_population,
                "confidence_lower": forecast.confidence_lower,
                "confidence_upper": forecast.confidence_upper,
                "age_breakdown": {
                    "age_0_14": forecast.predicted_age_0_14,
                    "age_15_64": forecast.predicted_age_15_64,
                    "age_65_plus": forecast.predicted_age_65_plus
                },
                "model_info": {
                    "model_name": forecast.model_name,
                    "model_version": forecast.model_version,
                    "prediction_date": forecast.prediction_date
                }
            })
        
        return result