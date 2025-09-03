import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer
import warnings

logger = logging.getLogger(__name__)

class DataCleaner:
    """統計データのクリーニング・前処理クラス"""
    
    def __init__(self):
        self.scalers = {}
        self.imputers = {}
        
    def handle_missing_values(self, 
                            df: pd.DataFrame, 
                            strategy: str = "mean",
                            columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        欠損値処理
        
        Args:
            df: 対象データフレーム
            strategy: 補完戦略 ("mean", "median", "mode", "knn", "forward_fill", "drop")
            columns: 対象列（Noneの場合は数値列全て）
            
        Returns:
            欠損値処理済みのDataFrame
        """
        try:
            df_processed = df.copy()
            
            if columns is None:
                # 数値列のみを対象
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                columns = numeric_columns
            
            logger.info(f"欠損値処理開始: {strategy}戦略, 対象列数: {len(columns)}")
            
            if strategy == "drop":
                # 欠損値を含む行を削除
                df_processed = df_processed.dropna(subset=columns)
                
            elif strategy == "forward_fill":
                # 前方補完
                df_processed[columns] = df_processed[columns].fillna(method='ffill')
                
            elif strategy == "knn":
                # KNN補完
                imputer = KNNImputer(n_neighbors=5)
                df_processed[columns] = imputer.fit_transform(df_processed[columns])
                self.imputers["knn"] = imputer
                
            else:
                # SimpleImputer使用（mean, median, mode）
                if strategy == "mode":
                    imputer = SimpleImputer(strategy="most_frequent")
                else:
                    imputer = SimpleImputer(strategy=strategy)
                
                df_processed[columns] = imputer.fit_transform(df_processed[columns])
                self.imputers[strategy] = imputer
            
            # 結果確認
            missing_after = df_processed[columns].isnull().sum().sum()
            logger.info(f"欠損値処理完了: 残り欠損値数 {missing_after}")
            
            return df_processed
            
        except Exception as e:
            logger.error(f"欠損値処理エラー: {e}")
            raise
    
    def detect_outliers(self, 
                       df: pd.DataFrame, 
                       columns: Optional[List[str]] = None,
                       method: str = "iqr") -> pd.DataFrame:
        """
        異常値検出
        
        Args:
            df: 対象データフレーム
            columns: 対象列
            method: 検出手法 ("iqr", "zscore", "isolation_forest")
            
        Returns:
            異常値フラグを含むDataFrame
        """
        try:
            df_processed = df.copy()
            
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            logger.info(f"異常値検出開始: {method}手法")
            
            for col in columns:
                if method == "iqr":
                    # IQR法
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
                    df_processed[f"{col}_outlier"] = outliers
                    
                elif method == "zscore":
                    # Z-score法
                    z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                    outliers = z_scores > 3
                    df_processed[f"{col}_outlier"] = outliers
                
                elif method == "isolation_forest":
                    # Isolation Forest
                    from sklearn.ensemble import IsolationForest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    outliers = iso_forest.fit_predict(df[[col]].values.reshape(-1, 1)) == -1
                    df_processed[f"{col}_outlier"] = outliers
            
            # 異常値統計
            outlier_cols = [col for col in df_processed.columns if col.endswith('_outlier')]
            total_outliers = df_processed[outlier_cols].sum().sum()
            logger.info(f"異常値検出完了: 総異常値数 {total_outliers}")
            
            return df_processed
            
        except Exception as e:
            logger.error(f"異常値検出エラー: {e}")
            raise
    
    def normalize_data(self, 
                      df: pd.DataFrame, 
                      columns: Optional[List[str]] = None,
                      method: str = "standard") -> pd.DataFrame:
        """
        データ正規化・スケーリング
        
        Args:
            df: 対象データフレーム
            columns: 対象列
            method: 正規化手法 ("standard", "minmax", "robust")
            
        Returns:
            正規化済みのDataFrame
        """
        try:
            df_processed = df.copy()
            
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            logger.info(f"データ正規化開始: {method}手法")
            
            if method == "standard":
                scaler = StandardScaler()
            elif method == "minmax":
                scaler = MinMaxScaler()
            elif method == "robust":
                scaler = RobustScaler()
            else:
                raise ValueError(f"未対応の正規化手法: {method}")
            
            # スケーリング実行
            df_processed[columns] = scaler.fit_transform(df_processed[columns])
            self.scalers[method] = scaler
            
            logger.info(f"データ正規化完了: {len(columns)}列処理")
            return df_processed
            
        except Exception as e:
            logger.error(f"データ正規化エラー: {e}")
            raise
    
    def create_time_features(self, 
                           df: pd.DataFrame, 
                           date_column: str) -> pd.DataFrame:
        """
        時系列特徴量生成
        
        Args:
            df: 対象データフレーム
            date_column: 日付列名
            
        Returns:
            時系列特徴量を追加したDataFrame
        """
        try:
            df_processed = df.copy()
            
            # 日付列をdatetimeに変換
            df_processed[date_column] = pd.to_datetime(df_processed[date_column])
            
            # 基本的な時系列特徴量
            df_processed['year'] = df_processed[date_column].dt.year
            df_processed['month'] = df_processed[date_column].dt.month
            df_processed['quarter'] = df_processed[date_column].dt.quarter
            df_processed['day_of_year'] = df_processed[date_column].dt.dayofyear
            
            # 曜日・週末フラグ
            df_processed['day_of_week'] = df_processed[date_column].dt.dayofweek
            df_processed['is_weekend'] = df_processed['day_of_week'].isin([5, 6]).astype(int)
            
            # 季節性特徴量
            df_processed['season'] = df_processed['month'].map({
                12: 'winter', 1: 'winter', 2: 'winter',
                3: 'spring', 4: 'spring', 5: 'spring',
                6: 'summer', 7: 'summer', 8: 'summer',
                9: 'autumn', 10: 'autumn', 11: 'autumn'
            })
            
            logger.info("時系列特徴量生成完了")
            return df_processed
            
        except Exception as e:
            logger.error(f"時系列特徴量生成エラー: {e}")
            raise
    
    def create_lag_features(self, 
                          df: pd.DataFrame, 
                          target_columns: List[str],
                          lags: List[int] = [1, 2, 3, 6, 12]) -> pd.DataFrame:
        """
        ラグ特徴量生成
        
        Args:
            df: 対象データフレーム
            target_columns: ラグを作成する列
            lags: ラグ期間のリスト
            
        Returns:
            ラグ特徴量を追加したDataFrame
        """
        try:
            df_processed = df.copy()
            
            for col in target_columns:
                for lag in lags:
                    df_processed[f"{col}_lag_{lag}"] = df_processed[col].shift(lag)
            
            logger.info(f"ラグ特徴量生成完了: {len(target_columns)}列 × {len(lags)}期間")
            return df_processed
            
        except Exception as e:
            logger.error(f"ラグ特徴量生成エラー: {e}")
            raise
    
    def create_rolling_features(self, 
                              df: pd.DataFrame, 
                              target_columns: List[str],
                              windows: List[int] = [3, 6, 12]) -> pd.DataFrame:
        """
        移動統計特徴量生成
        
        Args:
            df: 対象データフレーム
            target_columns: 対象列
            windows: 移動平均ウィンドウサイズのリスト
            
        Returns:
            移動統計特徴量を追加したDataFrame
        """
        try:
            df_processed = df.copy()
            
            for col in target_columns:
                for window in windows:
                    # 移動平均
                    df_processed[f"{col}_ma_{window}"] = df_processed[col].rolling(window=window).mean()
                    
                    # 移動標準偏差
                    df_processed[f"{col}_std_{window}"] = df_processed[col].rolling(window=window).std()
                    
                    # 移動最大値・最小値
                    df_processed[f"{col}_max_{window}"] = df_processed[col].rolling(window=window).max()
                    df_processed[f"{col}_min_{window}"] = df_processed[col].rolling(window=window).min()
            
            logger.info(f"移動統計特徴量生成完了: {len(target_columns)}列 × {len(windows)}ウィンドウ")
            return df_processed
            
        except Exception as e:
            logger.error(f"移動統計特徴量生成エラー: {e}")
            raise
    
    def comprehensive_preprocessing(self, 
                                  df: pd.DataFrame,
                                  date_column: Optional[str] = None,
                                  target_columns: Optional[List[str]] = None,
                                  missing_strategy: str = "mean",
                                  outlier_method: str = "iqr",
                                  scaling_method: str = "standard") -> pd.DataFrame:
        """
        包括的なデータ前処理
        
        Args:
            df: 対象データフレーム
            date_column: 日付列名
            target_columns: 主要分析対象列
            missing_strategy: 欠損値処理戦略
            outlier_method: 異常値検出手法
            scaling_method: スケーリング手法
            
        Returns:
            前処理済みのDataFrame
        """
        try:
            logger.info("包括的データ前処理開始")
            df_processed = df.copy()
            
            # 1. 欠損値処理
            df_processed = self.handle_missing_values(df_processed, strategy=missing_strategy)
            
            # 2. 異常値検出（フラグ付与のみ）
            df_processed = self.detect_outliers(df_processed, method=outlier_method)
            
            # 3. 時系列特徴量生成
            if date_column and date_column in df_processed.columns:
                df_processed = self.create_time_features(df_processed, date_column)
            
            # 4. ラグ・移動平均特徴量生成
            if target_columns:
                numeric_targets = [col for col in target_columns if col in df_processed.select_dtypes(include=[np.number]).columns]
                if numeric_targets:
                    df_processed = self.create_lag_features(df_processed, numeric_targets)
                    df_processed = self.create_rolling_features(df_processed, numeric_targets)
            
            # 5. データ正規化（数値列のみ）
            numeric_columns = df_processed.select_dtypes(include=[np.number]).columns.tolist()
            # 異常値フラグ列やカテゴリ変数を除外
            scaling_columns = [col for col in numeric_columns 
                             if not col.endswith('_outlier') and not col.startswith('is_') and col != 'year']
            
            if scaling_columns:
                df_processed = self.normalize_data(df_processed, scaling_columns, method=scaling_method)
            
            logger.info(f"包括的データ前処理完了: {df_processed.shape}")
            return df_processed
            
        except Exception as e:
            logger.error(f"包括的データ前処理エラー: {e}")
            raise
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        データ品質レポート生成
        
        Args:
            df: 対象データフレーム
            
        Returns:
            データ品質指標辞書
        """
        try:
            report = {}
            
            # 基本情報
            report['shape'] = df.shape
            report['memory_usage'] = df.memory_usage(deep=True).sum() / 1024**2  # MB
            
            # 欠損値情報
            missing_stats = df.isnull().sum()
            report['missing_values'] = {
                'total': missing_stats.sum(),
                'by_column': missing_stats[missing_stats > 0].to_dict(),
                'missing_rate': (missing_stats.sum() / df.size * 100)
            }
            
            # データタイプ情報
            report['data_types'] = df.dtypes.value_counts().to_dict()
            
            # 数値列統計
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                report['numeric_summary'] = {
                    'count': len(numeric_df.columns),
                    'stats': numeric_df.describe().to_dict()
                }
            
            # 重複行
            report['duplicated_rows'] = df.duplicated().sum()
            
            logger.info("データ品質レポート生成完了")
            return report
            
        except Exception as e:
            logger.error(f"データ品質レポート生成エラー: {e}")
            raise