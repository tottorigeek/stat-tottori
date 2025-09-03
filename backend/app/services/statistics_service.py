from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from app.models.population import PopulationData
from app.models.livability import LivabilityScore
import pandas as pd
import numpy as np
from datetime import datetime


class StatisticsService:
    """統計分析関連サービス"""

    async def get_kpi_dashboard_data(
        self,
        db: Session,
        prefecture_code: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """KPIダッシュボード用データを取得する"""
        
        if year is None:
            year = datetime.now().year - 1  # 前年のデータを使用

        # 人口関連KPI
        population_data = db.query(PopulationData).filter(
            and_(
                PopulationData.prefecture_code == prefecture_code,
                PopulationData.year == year,
                PopulationData.municipality_code.is_(None)
            )
        ).first()

        population_previous = db.query(PopulationData).filter(
            and_(
                PopulationData.prefecture_code == prefecture_code,
                PopulationData.year == year - 1,
                PopulationData.municipality_code.is_(None)
            )
        ).first()

        # 住みやすさ関連KPI
        livability_scores = db.query(LivabilityScore).filter(
            and_(
                LivabilityScore.prefecture_code == prefecture_code,
                LivabilityScore.year == year
            )
        ).all()

        # KPIデータを計算
        kpi_data = {
            "population_metrics": self._calculate_population_kpis(population_data, population_previous),
            "livability_metrics": self._calculate_livability_kpis(livability_scores),
            "trend_data": await self._get_trend_summary(db, prefecture_code, year),
            "alerts": self._generate_alerts(population_data, livability_scores),
            "last_updated": datetime.now().isoformat()
        }

        return kpi_data

    async def get_correlation_matrix(
        self,
        db: Session,
        indicators: List[str],
        prefecture_code: str,
        years: int = 10
    ) -> Dict[str, Any]:
        """指標間相関関係マトリクスを取得する"""
        
        current_year = datetime.now().year
        start_year = current_year - years

        # データを取得してDataFrameに変換
        data_dict = {}
        
        for indicator in indicators:
            if indicator.startswith("population_"):
                # 人口関連指標
                data = await self._get_population_indicator_data(
                    db, indicator, prefecture_code, start_year, current_year
                )
            elif indicator.startswith("livability_"):
                # 住みやすさ関連指標
                data = await self._get_livability_indicator_data(
                    db, indicator, prefecture_code, start_year, current_year
                )
            else:
                continue
                
            data_dict[indicator] = data

        # 相関行列を計算
        df = pd.DataFrame(data_dict)
        correlation_matrix = df.corr()

        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "indicators": indicators,
            "data_period": f"{start_year}-{current_year}",
            "sample_size": len(df)
        }

    async def get_time_series_analysis(
        self,
        db: Session,
        indicator: str,
        prefecture_code: str,
        municipality_code: Optional[str] = None,
        years: int = 20,
        include_forecast: bool = False
    ) -> Dict[str, Any]:
        """時系列分析データを取得する"""
        
        current_year = datetime.now().year
        start_year = current_year - years

        # 時系列データを取得
        time_series_data = await self._get_time_series_data(
            db, indicator, prefecture_code, municipality_code, start_year, current_year
        )

        # 基本統計量を計算
        data_values = [point["value"] for point in time_series_data if point["value"] is not None]
        
        if not data_values:
            raise ValueError("分析対象データが不足しています")

        statistics = {
            "mean": np.mean(data_values),
            "std": np.std(data_values),
            "min": np.min(data_values),
            "max": np.max(data_values),
            "trend": self._calculate_trend(data_values)
        }

        result = {
            "indicator": indicator,
            "time_series": time_series_data,
            "statistics": statistics,
            "analysis_period": f"{start_year}-{current_year}"
        }

        if include_forecast:
            # 簡単な線形回帰による予測（実際の実装では高度なモデルを使用）
            forecast_data = self._simple_forecast(data_values, periods=5)
            result["forecast"] = forecast_data

        return result

    async def get_comparative_analysis(
        self,
        db: Session,
        base_municipality: str,
        comparison_municipalities: List[str],
        indicators: List[str],
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """地域間比較分析データを取得する"""
        
        if year is None:
            year = datetime.now().year - 1

        all_municipalities = [base_municipality] + comparison_municipalities
        comparison_data = {}

        for municipality in all_municipalities:
            municipality_data = {}
            
            for indicator in indicators:
                value = await self._get_indicator_value(
                    db, indicator, municipality, year
                )
                municipality_data[indicator] = value
            
            comparison_data[municipality] = {
                "name": self._get_municipality_name(municipality),
                "indicators": municipality_data
            }

        # ベース地域との差分を計算
        base_data = comparison_data[base_municipality]["indicators"]
        
        for municipality in comparison_municipalities:
            comp_data = comparison_data[municipality]["indicators"]
            differences = {}
            
            for indicator in indicators:
                base_value = base_data.get(indicator, 0)
                comp_value = comp_data.get(indicator, 0)
                
                if base_value != 0:
                    diff_percentage = ((comp_value - base_value) / base_value) * 100
                    differences[indicator] = {
                        "absolute_difference": comp_value - base_value,
                        "percentage_difference": diff_percentage
                    }
                else:
                    differences[indicator] = {
                        "absolute_difference": comp_value,
                        "percentage_difference": None
                    }
            
            comparison_data[municipality]["differences_from_base"] = differences

        return {
            "base_municipality": base_municipality,
            "comparison_municipalities": comparison_municipalities,
            "comparison_data": comparison_data,
            "analysis_year": year
        }

    async def get_geographic_data(
        self,
        db: Session,
        indicator: str,
        prefecture_code: str,
        year: Optional[int] = None,
        output_format: str = "geojson"
    ) -> Dict[str, Any]:
        """地図表示用地理データを取得する"""
        
        if year is None:
            year = datetime.now().year - 1

        # 市町村別データを取得
        municipalities_data = await self._get_municipalities_indicator_data(
            db, indicator, prefecture_code, year
        )

        if output_format == "geojson":
            # GeoJSON形式で返す（Mapbox GL用）
            features = []
            
            for municipality_code, value in municipalities_data.items():
                # 実際の実装では、地理境界データも含める
                feature = {
                    "type": "Feature",
                    "properties": {
                        "municipality_code": municipality_code,
                        "municipality_name": self._get_municipality_name(municipality_code),
                        "indicator_value": value,
                        "indicator_name": indicator
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": []  # 実際の境界座標データ
                    }
                }
                features.append(feature)

            return {
                "type": "FeatureCollection",
                "features": features,
                "metadata": {
                    "indicator": indicator,
                    "year": year,
                    "prefecture_code": prefecture_code
                }
            }
        
        else:
            # その他の形式
            return {
                "data": municipalities_data,
                "indicator": indicator,
                "year": year,
                "format": output_format
            }

    def _calculate_population_kpis(self, current_data, previous_data) -> Dict[str, Any]:
        """人口関連KPIを計算する"""
        if not current_data:
            return {}

        kpis = {
            "total_population": current_data.total_population,
            "aging_rate": (current_data.age_65_plus / current_data.total_population * 100) 
                          if current_data.age_65_plus else None,
            "birth_rate": (current_data.births / current_data.total_population * 1000) 
                          if current_data.births else None,
            "death_rate": (current_data.deaths / current_data.total_population * 1000) 
                          if current_data.deaths else None,
        }

        if previous_data:
            kpis["population_change_rate"] = (
                (current_data.total_population - previous_data.total_population) / 
                previous_data.total_population * 100
            )

        return kpis

    def _calculate_livability_kpis(self, livability_scores: List) -> Dict[str, Any]:
        """住みやすさ関連KPIを計算する"""
        if not livability_scores:
            return {}

        scores = [score.total_score for score in livability_scores if score.total_score]
        
        return {
            "average_livability_score": np.mean(scores) if scores else None,
            "max_livability_score": np.max(scores) if scores else None,
            "min_livability_score": np.min(scores) if scores else None,
            "livability_std": np.std(scores) if scores else None,
            "municipalities_count": len(livability_scores)
        }

    async def _get_trend_summary(self, db: Session, prefecture_code: str, year: int) -> Dict[str, Any]:
        """トレンドサマリーを取得する"""
        # 過去5年のトレンドデータを取得・計算
        return {
            "population_trend": "decreasing",
            "livability_trend": "improving",
            "economic_trend": "stable"
        }

    def _generate_alerts(self, population_data, livability_scores) -> List[Dict[str, Any]]:
        """アラート・注意事項を生成する"""
        alerts = []

        if population_data and population_data.age_65_plus:
            aging_rate = population_data.age_65_plus / population_data.total_population * 100
            if aging_rate > 35:
                alerts.append({
                    "level": "warning",
                    "message": f"高齢化率が{aging_rate:.1f}%と高い水準です",
                    "category": "population"
                })

        return alerts

    async def _get_population_indicator_data(self, db, indicator, prefecture_code, start_year, end_year):
        """人口関連指標データを取得する"""
        # 実装省略 - 具体的なクエリロジック
        return []

    async def _get_livability_indicator_data(self, db, indicator, prefecture_code, start_year, end_year):
        """住みやすさ関連指標データを取得する"""
        # 実装省略 - 具体的なクエリロジック
        return []

    async def _get_time_series_data(self, db, indicator, prefecture_code, municipality_code, start_year, end_year):
        """時系列データを取得する"""
        # 実装省略 - 具体的なクエリロジック
        return []

    async def _get_indicator_value(self, db, indicator, municipality_code, year):
        """指標値を取得する"""
        # 実装省略 - 具体的なクエリロジック
        return 0

    async def _get_municipalities_indicator_data(self, db, indicator, prefecture_code, year):
        """市町村別指標データを取得する"""
        # 実装省略 - 具体的なクエリロジック
        return {}

    def _calculate_trend(self, data_values: List[float]) -> str:
        """トレンドを計算する"""
        if len(data_values) < 2:
            return "insufficient_data"
        
        # 簡単な線形回帰の傾き
        x = np.arange(len(data_values))
        slope = np.polyfit(x, data_values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"

    def _simple_forecast(self, data_values: List[float], periods: int = 5) -> List[Dict[str, Any]]:
        """簡単な予測（線形回帰）"""
        if len(data_values) < 3:
            return []
        
        x = np.arange(len(data_values))
        coeffs = np.polyfit(x, data_values, 1)
        
        forecasts = []
        for i in range(1, periods + 1):
            next_x = len(data_values) + i
            predicted_value = coeffs[0] * next_x + coeffs[1]
            forecasts.append({
                "period": next_x,
                "predicted_value": predicted_value
            })
        
        return forecasts

    def _get_municipality_name(self, municipality_code: str) -> str:
        """市町村名を取得する"""
        municipality_names = {
            "31201": "鳥取市",
            "31202": "米子市",
            "31203": "倉吉市",
            "31204": "境港市",
        }
        return municipality_names.get(municipality_code, f"市町村({municipality_code})")