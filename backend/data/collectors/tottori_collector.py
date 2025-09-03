import requests
import pandas as pd
import json
from typing import Dict, List, Optional, Union
import logging
from datetime import datetime
from pathlib import Path
import csv

logger = logging.getLogger(__name__)

class TottoriDataCollector:
    """鳥取県統計データ収集クラス"""
    
    def __init__(self, data_dir: str = "data/raw/tottori"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 鳥取県統計情報システムのエンドポイント（仮想）
        self.tottori_stats_url = "https://www.pref.tottori.lg.jp/statistics/api"
        
    def get_municipal_population_data(self) -> pd.DataFrame:
        """
        市町村別人口データを取得
        
        Returns:
            市町村別人口データのDataFrame
        """
        try:
            # 実際の鳥取県統計データ（CSVファイル等からの読み込みを想定）
            sample_data = {
                'municipality': ['鳥取市', '米子市', '倉吉市', '境港市', '岩美町', '若桜町', 
                               '智頭町', '八頭町', '三朝町', '湯梨浜町', '琴浦町', '北栄町',
                               '日吉津村', '大山町', '南部町', '伯耆町', '日南町', '日野町', '江府町'],
                'population_2020': [188087, 146558, 47333, 33585, 11084, 3089,
                                   6890, 15775, 6577, 16375, 17029, 14420,
                                   3394, 16654, 10254, 10849, 4565, 2962, 2927],
                'population_2015': [193717, 149313, 49044, 34174, 11668, 3465,
                                   7154, 16815, 6842, 16928, 17635, 14898,
                                   3452, 17040, 10679, 11224, 4827, 3160, 3078],
                'population_2010': [197190, 151436, 50720, 35025, 12451, 3915,
                                   7311, 17939, 7016, 17262, 18314, 15442,
                                   3486, 17275, 11013, 11509, 5204, 3397, 3223],
                'area_km2': [765.31, 132.42, 272.15, 29.17, 122.32, 199.28,
                           224.70, 206.71, 233.52, 77.94, 139.97, 57.15,
                           4.20, 189.83, 114.03, 139.44, 340.87, 133.98, 124.52]
            }
            
            df = pd.DataFrame(sample_data)
            
            # 人口密度計算
            df['density_2020'] = df['population_2020'] / df['area_km2']
            df['density_2015'] = df['population_2015'] / df['area_km2']
            df['density_2010'] = df['population_2010'] / df['area_km2']
            
            # 人口増減率計算
            df['growth_rate_2015_2020'] = ((df['population_2020'] - df['population_2015']) / df['population_2015'] * 100).round(2)
            df['growth_rate_2010_2015'] = ((df['population_2015'] - df['population_2010']) / df['population_2010'] * 100).round(2)
            
            logger.info(f"市町村別人口データ取得完了: {len(df)}件")
            return df
            
        except Exception as e:
            logger.error(f"市町村別人口データ取得エラー: {e}")
            raise
    
    def get_age_structure_data(self) -> pd.DataFrame:
        """
        年齢構造データを取得
        
        Returns:
            年齢構造データのDataFrame
        """
        try:
            # 年齢3区分別人口データ（サンプル）
            sample_data = {
                'municipality': ['鳥取市', '米子市', '倉吉市', '境港市', '岩美町', '若桜町',
                               '智頭町', '八頭町', '三朝町', '湯梨浜町', '琴浦町', '北栄町',
                               '日吉津村', '大山町', '南部町', '伯耆町', '日南町', '日野町', '江府町'],
                'age_0_14': [22896, 17834, 5312, 3716, 1088, 235,
                           617, 1565, 588, 1725, 1689, 1587,
                           445, 1733, 947, 1070, 346, 224, 231],
                'age_15_64': [108756, 86324, 25914, 18455, 5678, 1477,
                             3454, 8254, 3407, 8643, 9074, 8139,
                             2134, 9142, 5234, 5889, 2135, 1426, 1445],
                'age_65_over': [56435, 42400, 16107, 11414, 4318, 1377,
                               2819, 5956, 2582, 6007, 6266, 4694,
                               815, 5779, 4073, 3890, 2084, 1312, 1251]
            }
            
            df = pd.DataFrame(sample_data)
            
            # 総人口計算
            df['total_population'] = df['age_0_14'] + df['age_15_64'] + df['age_65_over']
            
            # 構成比計算
            df['ratio_0_14'] = (df['age_0_14'] / df['total_population'] * 100).round(2)
            df['ratio_15_64'] = (df['age_15_64'] / df['total_population'] * 100).round(2)
            df['ratio_65_over'] = (df['age_65_over'] / df['total_population'] * 100).round(2)
            
            # 高齢化率分類
            df['aging_category'] = df['ratio_65_over'].apply(self._classify_aging_rate)
            
            logger.info(f"年齢構造データ取得完了: {len(df)}件")
            return df
            
        except Exception as e:
            logger.error(f"年齢構造データ取得エラー: {e}")
            raise
    
    def get_economic_indicators(self) -> pd.DataFrame:
        """
        市町村別経済指標データを取得
        
        Returns:
            経済指標データのDataFrame
        """
        try:
            # 経済指標データ（サンプル）
            sample_data = {
                'municipality': ['鳥取市', '米子市', '倉吉市', '境港市', '岩美町', '若桜町',
                               '智頭町', '八頭町', '三朝町', '湯梨浜町', '琴浦町', '北栄町',
                               '日吉津村', '大山町', '南部町', '伯耆町', '日南町', '日野町', '江府町'],
                'gdp_per_capita': [3200, 3100, 2800, 3400, 2600, 2200,
                                 2400, 2500, 2700, 2900, 2750, 3050,
                                 4200, 2650, 2450, 2550, 2300, 2150, 2250],
                'employment_rate': [62.5, 65.2, 59.8, 68.3, 58.2, 55.1,
                                  56.7, 58.9, 61.2, 63.4, 60.8, 64.1,
                                  71.8, 59.5, 57.3, 58.7, 54.8, 53.2, 54.6],
                'business_count': [12456, 8934, 3567, 2234, 678, 189,
                                 445, 1234, 456, 1123, 1089, 987,
                                 234, 1034, 567, 678, 234, 156, 145],
                'agriculture_workers': [2345, 1678, 1234, 567, 456, 234,
                                      567, 890, 345, 567, 789, 678,
                                      89, 678, 456, 567, 345, 234, 189],
                'manufacturing_workers': [8934, 12345, 3456, 4567, 567, 123,
                                        234, 567, 234, 789, 567, 890,
                                        345, 456, 234, 345, 123, 89, 78]
            }
            
            df = pd.DataFrame(sample_data)
            
            # 1次産業比率
            df['agriculture_ratio'] = (df['agriculture_workers'] / 
                                     (df['agriculture_workers'] + df['manufacturing_workers']) * 100).round(2)
            
            # 製造業比率
            df['manufacturing_ratio'] = (df['manufacturing_workers'] / 
                                       (df['agriculture_workers'] + df['manufacturing_workers']) * 100).round(2)
            
            logger.info(f"経済指標データ取得完了: {len(df)}件")
            return df
            
        except Exception as e:
            logger.error(f"経済指標データ取得エラー: {e}")
            raise
    
    def get_livability_indicators(self) -> pd.DataFrame:
        """
        住みやすさ関連指標データを取得
        
        Returns:
            住みやすさ指標データのDataFrame
        """
        try:
            # 住みやすさ指標データ（サンプル）
            sample_data = {
                'municipality': ['鳥取市', '米子市', '倉吉市', '境港市', '岩美町', '若桜町',
                               '智頭町', '八頭町', '三朝町', '湯梨浜町', '琴浦町', '北栄町',
                               '日吉津村', '大山町', '南部町', '伯耆町', '日南町', '日野町', '江府町'],
                'hospitals_per_1000': [2.8, 3.1, 2.9, 3.4, 1.8, 1.2,
                                     1.5, 1.9, 2.2, 2.4, 2.1, 2.6,
                                     2.9, 2.0, 1.7, 1.8, 1.4, 1.1, 1.3],
                'schools_per_1000': [1.5, 1.7, 1.6, 1.8, 1.3, 0.9,
                                   1.0, 1.2, 1.4, 1.5, 1.3, 1.6,
                                   1.7, 1.2, 1.1, 1.1, 0.8, 0.7, 0.8],
                'parks_area_per_capita': [25.6, 23.4, 28.9, 21.7, 45.6, 67.8,
                                        56.7, 43.2, 52.3, 34.5, 38.9, 29.8,
                                        18.9, 48.7, 52.1, 44.3, 78.9, 89.4, 76.5],
                'crime_rate_per_1000': [3.2, 4.1, 2.8, 3.9, 1.2, 0.8,
                                      1.1, 1.5, 1.3, 2.1, 1.8, 2.3,
                                      2.8, 1.4, 1.0, 1.2, 0.6, 0.4, 0.5],
                'commute_time_minutes': [18.5, 16.8, 15.2, 17.3, 12.4, 8.9,
                                       10.3, 13.7, 11.8, 14.6, 16.1, 15.9,
                                       19.2, 12.8, 9.7, 11.4, 7.8, 6.5, 8.1]
            }
            
            df = pd.DataFrame(sample_data)
            
            logger.info(f"住みやすさ指標データ取得完了: {len(df)}件")
            return df
            
        except Exception as e:
            logger.error(f"住みやすさ指標データ取得エラー: {e}")
            raise
    
    def _classify_aging_rate(self, rate: float) -> str:
        """高齢化率による分類"""
        if rate >= 35:
            return "超高齢社会"
        elif rate >= 28:
            return "高度高齢社会" 
        elif rate >= 21:
            return "高齢社会"
        elif rate >= 14:
            return "高齢化社会"
        else:
            return "一般社会"
    
    def collect_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        全データを収集
        
        Returns:
            データタイプ別のDataFrame辞書
        """
        collected_data = {}
        
        try:
            logger.info("鳥取県データ収集開始...")
            
            # 各データセット収集
            collected_data["municipal_population"] = self.get_municipal_population_data()
            collected_data["age_structure"] = self.get_age_structure_data()
            collected_data["economic_indicators"] = self.get_economic_indicators()
            collected_data["livability_indicators"] = self.get_livability_indicators()
            
            logger.info("鳥取県データ収集完了")
            return collected_data
            
        except Exception as e:
            logger.error(f"鳥取県データ収集エラー: {e}")
            raise
    
    def save_data(self, data_dict: Dict[str, pd.DataFrame]) -> None:
        """
        収集したデータをCSVファイルに保存
        
        Args:
            data_dict: データタイプ別のDataFrame辞書
        """
        try:
            for data_type, df in data_dict.items():
                file_path = self.data_dir / f"tottori_{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"データ保存完了: {file_path}")
                
        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
            raise