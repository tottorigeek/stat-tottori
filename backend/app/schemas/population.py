from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class PopulationBase(BaseModel):
    """人口データ基底モデル"""
    prefecture_code: str
    municipality_code: Optional[str] = None
    year: int
    month: Optional[int] = None
    total_population: int


class PopulationResponse(PopulationBase):
    """人口データレスポンスモデル"""
    id: int
    male_population: Optional[int] = None
    female_population: Optional[int] = None
    age_0_14: Optional[int] = None
    age_15_64: Optional[int] = None
    age_65_plus: Optional[int] = None
    births: Optional[int] = None
    deaths: Optional[int] = None
    natural_increase: Optional[int] = None
    in_migration: Optional[int] = None
    out_migration: Optional[int] = None
    net_migration: Optional[int] = None
    data_source: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PopulationSummary(BaseModel):
    """人口サマリーモデル"""
    prefecture_code: str
    year: int
    total_population: int
    population_change_rate: Optional[float] = None  # 前年比増減率
    aging_rate: Optional[float] = None  # 高齢化率
    birth_rate: Optional[float] = None  # 出生率
    death_rate: Optional[float] = None  # 死亡率
    migration_rate: Optional[float] = None  # 社会増減率
    
    # 年齢階層別構成比
    youth_ratio: Optional[float] = None  # 年少人口比率
    working_age_ratio: Optional[float] = None  # 生産年齢人口比率
    elderly_ratio: Optional[float] = None  # 老年人口比率


class PopulationForecastResponse(BaseModel):
    """人口予測レスポンスモデル"""
    id: int
    prefecture_code: str
    municipality_code: Optional[str] = None
    target_year: int
    predicted_population: int
    confidence_lower: Optional[int] = None
    confidence_upper: Optional[int] = None
    predicted_age_0_14: Optional[int] = None
    predicted_age_15_64: Optional[int] = None
    predicted_age_65_plus: Optional[int] = None
    model_name: str
    model_version: Optional[str] = None
    prediction_date: datetime
    
    class Config:
        from_attributes = True