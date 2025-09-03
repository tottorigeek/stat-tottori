from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class LivabilityScore(Base):
    """住みやすさスコアモデル"""
    __tablename__ = "livability_scores"

    id = Column(Integer, primary_key=True, index=True)
    prefecture_code = Column(String(2), nullable=False)
    municipality_code = Column(String(5), nullable=True)
    year = Column(Integer, nullable=False)
    
    # 総合スコア
    total_score = Column(Float, nullable=False)
    weighted_score = Column(Float, nullable=True)  # 重み付けスコア
    
    # カテゴリー別スコア
    infrastructure_score = Column(Float, nullable=True)  # インフラ
    healthcare_score = Column(Float, nullable=True)      # 医療・健康
    education_score = Column(Float, nullable=True)       # 教育
    environment_score = Column(Float, nullable=True)     # 環境
    economy_score = Column(Float, nullable=True)         # 経済・雇用
    community_score = Column(Float, nullable=True)       # コミュニティ
    transport_score = Column(Float, nullable=True)       # 交通
    culture_score = Column(Float, nullable=True)         # 文化・娯楽
    
    # 詳細指標（JSON形式で格納）
    detailed_metrics = Column(JSON, nullable=True)
    
    # 算出方法情報
    calculation_method = Column(String(50), nullable=True)
    weight_profile = Column(String(50), nullable=True)  # 重み付けプロファイル
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LivabilityIndicator(Base):
    """住みやすさ指標マスターデータ"""
    __tablename__ = "livability_indicators"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # カテゴリー
    indicator_name = Column(String(100), nullable=False)  # 指標名
    indicator_code = Column(String(50), nullable=False, unique=True)  # 指標コード
    
    # 指標詳細
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=True)  # 単位
    data_source = Column(String(100), nullable=True)
    calculation_formula = Column(Text, nullable=True)
    
    # 評価設定
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    optimal_value = Column(Float, nullable=True)
    higher_is_better = Column(Boolean, default=True)
    
    # 重み設定
    default_weight = Column(Float, default=1.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserLivabilityWeight(Base):
    """ユーザー個別の住みやすさ重み設定"""
    __tablename__ = "user_livability_weights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ユーザーID
    profile_name = Column(String(100), nullable=True)  # プロファイル名
    
    # カテゴリー別重み
    infrastructure_weight = Column(Float, default=1.0)
    healthcare_weight = Column(Float, default=1.0)
    education_weight = Column(Float, default=1.0)
    environment_weight = Column(Float, default=1.0)
    economy_weight = Column(Float, default=1.0)
    community_weight = Column(Float, default=1.0)
    transport_weight = Column(Float, default=1.0)
    culture_weight = Column(Float, default=1.0)
    
    # 詳細重み（JSON形式）
    detailed_weights = Column(JSON, nullable=True)
    
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())