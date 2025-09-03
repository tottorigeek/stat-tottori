import pytest
from app.models.population import PopulationData


class TestPopulationAPI:
    """人口データAPI のテストクラス"""

    def test_get_population_data_success(self, client, db, sample_population_data):
        """人口データ取得の正常ケーステスト"""
        # テストデータをデータベースに挿入
        population = PopulationData(**sample_population_data)
        db.add(population)
        db.commit()

        # APIエンドポイントをテスト
        response = client.get("/api/v1/population/?prefecture_code=31")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["total_population"] == 540000
        assert data[0]["prefecture_code"] == "31"

    def test_get_population_data_with_municipality_filter(self, client, db, sample_population_data):
        """市町村コードでフィルターした人口データ取得テスト"""
        # 市町村データを追加
        sample_population_data["municipality_code"] = "31201"
        population = PopulationData(**sample_population_data)
        db.add(population)
        db.commit()

        response = client.get("/api/v1/population/?prefecture_code=31&municipality_code=31201")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["municipality_code"] == "31201"

    def test_get_population_data_with_year_range(self, client, db, sample_population_data):
        """年範囲指定での人口データ取得テスト"""
        # 複数年のデータを挿入
        for year in [2021, 2022, 2023]:
            data = sample_population_data.copy()
            data["year"] = year
            data["total_population"] = 540000 + (year - 2021) * 1000
            population = PopulationData(**data)
            db.add(population)
        db.commit()

        response = client.get("/api/v1/population/?prefecture_code=31&year_start=2022&year_end=2023")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        years = [item["year"] for item in data]
        assert 2022 in years
        assert 2023 in years
        assert 2021 not in years

    def test_get_population_summary_success(self, client, db, sample_population_data):
        """人口サマリー取得の正常ケーステスト"""
        # 現在年と前年のデータを挿入
        current_year_data = sample_population_data.copy()
        current_year_data["year"] = 2023
        current_year_data["total_population"] = 540000
        
        previous_year_data = sample_population_data.copy()  
        previous_year_data["year"] = 2022
        previous_year_data["total_population"] = 545000
        
        db.add(PopulationData(**current_year_data))
        db.add(PopulationData(**previous_year_data))
        db.commit()

        response = client.get("/api/v1/population/summary?prefecture_code=31&year=2023")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_population"] == 540000
        assert data["year"] == 2023
        assert "population_change_rate" in data
        assert "aging_rate" in data

    def test_get_population_trend_chart_data(self, client, db, sample_population_data):
        """人口推移チャートデータ取得テスト"""
        # 複数年のトレンドデータを挿入
        for year in range(2019, 2024):
            data = sample_population_data.copy()
            data["year"] = year
            data["total_population"] = 560000 - (year - 2019) * 5000  # 減少トレンド
            data["age_15_64"] = 320000 - (year - 2019) * 3000
            data["age_65_plus"] = 150000 + (year - 2019) * 2000
            population = PopulationData(**data)
            db.add(population)
        db.commit()

        response = client.get("/api/v1/population/trend?prefecture_code=31&years=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "datasets" in data
        assert len(data["labels"]) == 5
        assert len(data["datasets"]) == 3  # 総人口、生産年齢人口、老年人口
        
        # チャートデータ形式の確認
        total_population_dataset = data["datasets"][0]
        assert total_population_dataset["label"] == "総人口"
        assert "borderColor" in total_population_dataset
        assert len(total_population_dataset["data"]) == 5

    def test_get_population_forecast(self, client):
        """人口予測データ取得テスト"""
        response = client.get("/api/v1/population/forecast?prefecture_code=31&years_ahead=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_population_data_empty_result(self, client):
        """データが存在しない場合のテスト"""
        response = client.get("/api/v1/population/?prefecture_code=99")  # 存在しない都道府県コード
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_population_data_invalid_parameters(self, client):
        """不正なパラメータでのテスト"""
        # 不正な年範囲
        response = client.get("/api/v1/population/?prefecture_code=31&year_start=2025&year_end=2020")
        assert response.status_code == 200  # エラーにはならないが空の結果

        # 不正な都道府県コード形式
        response = client.get("/api/v1/population/?prefecture_code=invalid")
        assert response.status_code == 200

    def test_population_summary_calculation_accuracy(self, client, db, sample_population_data):
        """人口サマリーの計算精度テスト"""
        population_data = sample_population_data.copy()
        population_data["total_population"] = 1000
        population_data["age_65_plus"] = 300  # 30%の高齢化率
        population_data["births"] = 10
        population_data["deaths"] = 15
        
        population = PopulationData(**population_data)
        db.add(population)
        db.commit()

        response = client.get("/api/v1/population/summary?prefecture_code=31&year=2023")
        
        assert response.status_code == 200
        data = response.json()
        
        # 高齢化率の計算確認 (300/1000 * 100 = 30.0)
        assert abs(data["aging_rate"] - 30.0) < 0.01
        
        # 出生率の計算確認 (10/1000 * 1000 = 10.0)
        assert abs(data["birth_rate"] - 10.0) < 0.01
        
        # 死亡率の計算確認 (15/1000 * 1000 = 15.0) 
        assert abs(data["death_rate"] - 15.0) < 0.01