from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class PopulationData(Base):
    """人口データモデル"""
    __tablename__ = "population_data"

    id = Column(Integer, primary_key=True, index=True)
    prefecture_code = Column(String(2), nullable=False)  # 都道府県コード
    municipality_code = Column(String(5), nullable=True)  # 市町村コード
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)  # 月次データの場合
    
    # 人口データ
    total_population = Column(Integer, nullable=False)
    male_population = Column(Integer, nullable=True)
    female_population = Column(Integer, nullable=True)
    
    # 年齢階層別人口
    age_0_14 = Column(Integer, nullable=True)  # 年少人口
    age_15_64 = Column(Integer, nullable=True)  # 生産年齢人口
    age_65_plus = Column(Integer, nullable=True)  # 老年人口
    
    # 自然動態
    births = Column(Integer, nullable=True)
    deaths = Column(Integer, nullable=True)
    natural_increase = Column(Integer, nullable=True)
    
    # 社会動態
    in_migration = Column(Integer, nullable=True)
    out_migration = Column(Integer, nullable=True)
    net_migration = Column(Integer, nullable=True)
    
    # データソース情報
    data_source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PopulationForecast(Base):
    """人口予測データモデル"""
    __tablename__ = "population_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    prefecture_code = Column(String(2), nullable=False)
    municipality_code = Column(String(5), nullable=True)
    target_year = Column(Integer, nullable=False)
    
    # 予測値
    predicted_population = Column(Integer, nullable=False)
    confidence_lower = Column(Integer, nullable=True)  # 信頼区間下限
    confidence_upper = Column(Integer, nullable=True)  # 信頼区間上限
    
    # 年齢階層別予測
    predicted_age_0_14 = Column(Integer, nullable=True)
    predicted_age_15_64 = Column(Integer, nullable=True)
    predicted_age_65_plus = Column(Integer, nullable=True)
    
    # モデル情報
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=True)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())