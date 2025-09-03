import requests
import pandas as pd
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class EstatCollector:
    """e-Stat API からの政府統計データ収集クラス"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.e-stat.go.jp/rest/3.0/app/json"
        self.session = requests.Session()
        
    def get_population_data(self, prefecture_code: str = "31", years: List[int] = None) -> pd.DataFrame:
        """
        人口データを取得
        
        Args:
            prefecture_code: 都道府県コード（鳥取県: 31）
            years: 取得対象年のリスト
            
        Returns:
            人口データのDataFrame
        """
        try:
            # 国勢調査データ（statsDataId: 0003448233 - 令和2年国勢調査）
            stats_data_id = "0003448233"
            
            params = {
                "appId": self.api_key,
                "statsDataId": stats_data_id,
                "metaGetFlg": "Y",
                "cdArea": f"{prefecture_code}000",  # 鳥取県全体
                "format": "json"
            }
            
            response = self.session.get(f"{self.base_url}/getStatsData", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # データ解析・変換
            if "GET_STATS_DATA" in data:
                stats_data = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
                df = pd.DataFrame(stats_data)
                
                # データ型変換
                df["@time"] = pd.to_datetime(df["@time"], format="%Y")
                df["$"] = pd.to_numeric(df["$"], errors="coerce")
                
                logger.info(f"人口データ取得完了: {len(df)}件")
                return df
            else:
                logger.warning("データが見つかりませんでした")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"人口データ取得エラー: {e}")
            raise
    
    def get_economic_data(self, prefecture_code: str = "31", indicator: str = "GDP") -> pd.DataFrame:
        """
        経済データを取得
        
        Args:
            prefecture_code: 都道府県コード
            indicator: 経済指標（GDP, 所得等）
            
        Returns:
            経済データのDataFrame
        """
        try:
            # 県民経済計算（statsDataId: 0003409428）
            stats_data_id = "0003409428"
            
            params = {
                "appId": self.api_key,
                "statsDataId": stats_data_id,
                "cdArea": f"{prefecture_code}000",
                "format": "json"
            }
            
            response = self.session.get(f"{self.base_url}/getStatsData", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "GET_STATS_DATA" in data:
                stats_data = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
                df = pd.DataFrame(stats_data)
                
                # データ変換
                df["@time"] = pd.to_datetime(df["@time"], format="%Y")
                df["$"] = pd.to_numeric(df["$"], errors="coerce")
                
                logger.info(f"経済データ取得完了: {len(df)}件")
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"経済データ取得エラー: {e}")
            raise
    
    def get_employment_data(self, prefecture_code: str = "31") -> pd.DataFrame:
        """
        雇用・労働データを取得
        
        Args:
            prefecture_code: 都道府県コード
            
        Returns:
            雇用データのDataFrame
        """
        try:
            # 労働力調査（statsDataId: 0003137815）
            stats_data_id = "0003137815"
            
            params = {
                "appId": self.api_key,
                "statsDataId": stats_data_id,
                "cdArea": f"{prefecture_code}000",
                "format": "json"
            }
            
            response = self.session.get(f"{self.base_url}/getStatsData", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "GET_STATS_DATA" in data:
                stats_data = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
                df = pd.DataFrame(stats_data)
                
                df["@time"] = pd.to_datetime(df["@time"], format="%Y-%m")
                df["$"] = pd.to_numeric(df["$"], errors="coerce")
                
                logger.info(f"雇用データ取得完了: {len(df)}件")
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"雇用データ取得エラー: {e}")
            raise
    
    def get_statistical_categories(self) -> pd.DataFrame:
        """
        利用可能な統計データのカテゴリ一覧を取得
        
        Returns:
            統計カテゴリのDataFrame
        """
        try:
            params = {
                "appId": self.api_key,
                "lang": "J",
                "format": "json"
            }
            
            response = self.session.get(f"{self.base_url}/getStatsList", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "GET_STATS_LIST" in data:
                stats_list = data["GET_STATS_LIST"]["DATALIST_INF"]["TABLE_INF"]
                df = pd.DataFrame(stats_list)
                
                logger.info(f"統計カテゴリ取得完了: {len(df)}件")
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"統計カテゴリ取得エラー: {e}")
            raise
    
    def rate_limit_wait(self, wait_seconds: float = 1.0):
        """APIレート制限対応の待機"""
        time.sleep(wait_seconds)
    
    def collect_comprehensive_data(self, prefecture_code: str = "31") -> Dict[str, pd.DataFrame]:
        """
        包括的な統計データを収集
        
        Args:
            prefecture_code: 都道府県コード
            
        Returns:
            データタイプ別のDataFrame辞書
        """
        collected_data = {}
        
        try:
            # 人口データ
            logger.info("人口データ収集開始...")
            collected_data["population"] = self.get_population_data(prefecture_code)
            self.rate_limit_wait()
            
            # 経済データ
            logger.info("経済データ収集開始...")
            collected_data["economy"] = self.get_economic_data(prefecture_code)
            self.rate_limit_wait()
            
            # 雇用データ
            logger.info("雇用データ収集開始...")
            collected_data["employment"] = self.get_employment_data(prefecture_code)
            
            logger.info("全データ収集完了")
            return collected_data
            
        except Exception as e:
            logger.error(f"包括的データ収集エラー: {e}")
            raise