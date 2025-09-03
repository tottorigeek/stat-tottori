from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class LivabilityScoreBase(BaseModel):
    """住みやすさスコア基底モデル"""
    prefecture_code: str
    municipality_code: Optional[str] = None
    year: int
    total_score: float


class LivabilityScoreResponse(LivabilityScoreBase):
    """住みやすさスコアレスポンスモデル"""
    id: int
    weighted_score: Optional[float] = None
    infrastructure_score: Optional[float] = None
    healthcare_score: Optional[float] = None
    education_score: Optional[float] = None
    environment_score: Optional[float] = None
    economy_score: Optional[float] = None
    community_score: Optional[float] = None
    transport_score: Optional[float] = None
    culture_score: Optional[float] = None
    detailed_metrics: Optional[Dict[str, Any]] = None
    calculation_method: Optional[str] = None
    weight_profile: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LivabilityIndicatorResponse(BaseModel):
    """住みやすさ指標レスポンスモデル"""
    id: int
    category: str
    indicator_name: str
    indicator_code: str
    description: Optional[str] = None
    unit: Optional[str] = None
    data_source: Optional[str] = None
    calculation_formula: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    optimal_value: Optional[float] = None
    higher_is_better: bool = True
    default_weight: float = 1.0
    is_active: bool = True
    
    class Config:
        from_attributes = True


class LivabilityComparisonResponse(BaseModel):
    """住みやすさ比較レスポンスモデル"""
    municipality_code: str
    municipality_name: str
    total_score: float
    category_scores: Dict[str, float]
    rank: Optional[int] = None
    percentile: Optional[float] = None


class UserWeightProfile(BaseModel):
    """ユーザー重み設定モデル"""
    user_id: int
    profile_name: Optional[str] = None
    infrastructure_weight: float = 1.0
    healthcare_weight: float = 1.0
    education_weight: float = 1.0
    environment_weight: float = 1.0
    economy_weight: float = 1.0
    community_weight: float = 1.0
    transport_weight: float = 1.0
    culture_weight: float = 1.0
    detailed_weights: Optional[Dict[str, float]] = None
    is_default: bool = False