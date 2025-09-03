import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base

# テスト用のSQLiteデータベースを使用
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """テスト用データベースセッション"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# データベース依存関係をオーバーライド
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    """テストクライアントを提供"""
    # テスト用データベーステーブルを作成
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # テスト後にテーブルを削除
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """テスト用データベースセッションを提供"""
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        

@pytest.fixture
def sample_population_data():
    """サンプル人口データ"""
    return {
        "prefecture_code": "31",
        "municipality_code": None,
        "year": 2023,
        "total_population": 540000,
        "male_population": 260000,
        "female_population": 280000,
        "age_0_14": 65000,
        "age_15_64": 310000,
        "age_65_plus": 165000,
        "births": 3500,
        "deaths": 7500,
        "natural_increase": -4000,
        "in_migration": 12000,
        "out_migration": 15000,
        "net_migration": -3000,
        "data_source": "test_data"
    }


@pytest.fixture
def sample_livability_data():
    """サンプル住みやすさデータ"""
    return {
        "prefecture_code": "31",
        "municipality_code": "31201",
        "year": 2023,
        "total_score": 75.5,
        "infrastructure_score": 80.0,
        "healthcare_score": 70.0,
        "education_score": 85.0,
        "environment_score": 75.0,
        "economy_score": 65.0,
        "community_score": 80.0,
        "transport_score": 60.0,
        "culture_score": 70.0,
        "calculation_method": "weighted_average",
        "weight_profile": "default"
    }