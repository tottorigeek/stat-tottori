import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import joblib
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class PopulationPredictor:
    """人口動態予測モデルクラス"""
    
    def __init__(self, model_dir: str = "backend/data/models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
        # モデル設定
        self.model_configs = {
            'xgboost': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            },
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42
            }
        }
        
    def prepare_features(self, df: pd.DataFrame, 
                        target_column: str = 'population',
                        date_column: str = 'date') -> Tuple[pd.DataFrame, pd.Series]:
        """
        予測用特徴量準備
        
        Args:
            df: 入力データフレーム
            target_column: 目的変数列名
            date_column: 日付列名
            
        Returns:
            特徴量データフレームと目的変数シリーズ
        """
        try:
            df_processed = df.copy()
            
            # 日付特徴量
            if date_column in df_processed.columns:
                df_processed[date_column] = pd.to_datetime(df_processed[date_column])
                df_processed['year'] = df_processed[date_column].dt.year
                df_processed['month'] = df_processed[date_column].dt.month
                df_processed['quarter'] = df_processed[date_column].dt.quarter
            
            # ラグ特徴量
            for lag in [1, 2, 3, 5]:
                df_processed[f'{target_column}_lag_{lag}'] = df_processed[target_column].shift(lag)
            
            # 移動平均特徴量
            for window in [3, 5, 10]:
                df_processed[f'{target_column}_ma_{window}'] = df_processed[target_column].rolling(window=window).mean()
                df_processed[f'{target_column}_std_{window}'] = df_processed[target_column].rolling(window=window).std()
            
            # 人口増減率
            df_processed[f'{target_column}_pct_change'] = df_processed[target_column].pct_change()
            df_processed[f'{target_column}_diff'] = df_processed[target_column].diff()
            
            # トレンド特徴量
            df_processed['trend'] = np.arange(len(df_processed))
            df_processed['trend_squared'] = df_processed['trend'] ** 2
            
            # 特徴量列選択
            feature_columns = [col for col in df_processed.columns 
                             if col not in [target_column, date_column] and not col.startswith('Unnamed')]
            
            X = df_processed[feature_columns].fillna(method='bfill').fillna(method='ffill')
            y = df_processed[target_column]
            
            self.feature_columns = feature_columns
            
            logger.info(f"特徴量準備完了: {X.shape[1]}個の特徴量")
            return X, y
            
        except Exception as e:
            logger.error(f"特徴量準備エラー: {e}")
            raise
    
    def fit_arima(self, data: pd.Series, order: Tuple[int, int, int] = (2, 1, 2)) -> Dict:
        """
        ARIMAモデルの学習
        
        Args:
            data: 時系列データ
            order: ARIMA次数 (p, d, q)
            
        Returns:
            学習済みモデルと評価指標
        """
        try:
            logger.info(f"ARIMAモデル学習開始: order={order}")
            
            # データ分割（80%学習、20%テスト）
            train_size = int(len(data) * 0.8)
            train_data = data[:train_size]
            test_data = data[train_size:]
            
            # モデル学習
            model = ARIMA(train_data, order=order)
            fitted_model = model.fit()
            
            # 予測
            forecast = fitted_model.forecast(steps=len(test_data))
            
            # 評価指標計算
            mae = mean_absolute_error(test_data, forecast)
            mse = mean_squared_error(test_data, forecast)
            rmse = np.sqrt(mse)
            
            # モデル保存
            self.models['arima'] = fitted_model
            
            result = {
                'model': fitted_model,
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'forecast': forecast,
                'test_data': test_data,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic
            }
            
            logger.info(f"ARIMAモデル学習完了: MAE={mae:.2f}, RMSE={rmse:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"ARIMAモデル学習エラー: {e}")
            raise
    
    def fit_xgboost(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        XGBoostモデルの学習
        
        Args:
            X: 特徴量データフレーム
            y: 目的変数シリーズ
            
        Returns:
            学習済みモデルと評価指標
        """
        try:
            logger.info("XGBoostモデル学習開始")
            
            # 時系列分割
            tscv = TimeSeriesSplit(n_splits=5)
            
            # モデル定義
            model = xgb.XGBRegressor(**self.model_configs['xgboost'])
            
            # 交差検証
            cv_scores = []
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                mae = mean_absolute_error(y_test, y_pred)
                cv_scores.append(mae)
            
            # 全データで再学習
            model.fit(X, y)
            
            # 特徴量重要度
            feature_importance = dict(zip(X.columns, model.feature_importances_))
            
            # モデル保存
            self.models['xgboost'] = model
            
            result = {
                'model': model,
                'cv_mae_mean': np.mean(cv_scores),
                'cv_mae_std': np.std(cv_scores),
                'feature_importance': feature_importance
            }
            
            logger.info(f"XGBoostモデル学習完了: CV MAE={np.mean(cv_scores):.2f}±{np.std(cv_scores):.2f}")
            return result
            
        except Exception as e:
            logger.error(f"XGBoostモデル学習エラー: {e}")
            raise
    
    def fit_random_forest(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Random Forestモデルの学習
        
        Args:
            X: 特徴量データフレーム
            y: 目的変数シリーズ
            
        Returns:
            学習済みモデルと評価指標
        """
        try:
            logger.info("Random Forestモデル学習開始")
            
            # 時系列分割
            tscv = TimeSeriesSplit(n_splits=5)
            
            # モデル定義
            model = RandomForestRegressor(**self.model_configs['random_forest'])
            
            # 交差検証
            cv_scores = []
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                mae = mean_absolute_error(y_test, y_pred)
                cv_scores.append(mae)
            
            # 全データで再学習
            model.fit(X, y)
            
            # 特徴量重要度
            feature_importance = dict(zip(X.columns, model.feature_importances_))
            
            # モデル保存
            self.models['random_forest'] = model
            
            result = {
                'model': model,
                'cv_mae_mean': np.mean(cv_scores),
                'cv_mae_std': np.std(cv_scores),
                'feature_importance': feature_importance
            }
            
            logger.info(f"Random Forestモデル学習完了: CV MAE={np.mean(cv_scores):.2f}±{np.std(cv_scores):.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Random Forestモデル学習エラー: {e}")
            raise
    
    def predict_population(self, 
                          model_type: str,
                          years_ahead: int = 10,
                          policy_scenario: Optional[Dict] = None) -> Dict:
        """
        人口予測実行
        
        Args:
            model_type: 使用モデル ("arima", "xgboost", "random_forest", "ensemble")
            years_ahead: 予測期間（年）
            policy_scenario: 政策シナリオ（政策効果を加味）
            
        Returns:
            予測結果辞書
        """
        try:
            logger.info(f"{model_type}モデルによる{years_ahead}年先予測開始")
            
            if model_type not in self.models:
                raise ValueError(f"学習済みモデルが見つかりません: {model_type}")
            
            model = self.models[model_type]
            
            if model_type == 'arima':
                # ARIMA予測
                forecast = model.forecast(steps=years_ahead * 12)  # 月次予測
                confidence_intervals = model.get_forecast(steps=years_ahead * 12).conf_int()
                
                result = {
                    'forecast': forecast.values,
                    'lower_bound': confidence_intervals.iloc[:, 0].values,
                    'upper_bound': confidence_intervals.iloc[:, 1].values,
                    'dates': pd.date_range(start=datetime.now(), periods=years_ahead * 12, freq='M')
                }
                
            else:
                # 機械学習モデル予測
                # 最新データから特徴量を構築して予測（簡略化）
                # 実際の実装では、最新データから将来の特徴量を推定する必要がある
                
                result = {
                    'forecast': [100000] * years_ahead,  # プレースホルダー
                    'dates': pd.date_range(start=datetime.now(), periods=years_ahead, freq='Y')
                }
            
            # 政策効果を加味
            if policy_scenario:
                result = self._apply_policy_effects(result, policy_scenario)
            
            logger.info(f"人口予測完了: {model_type}")
            return result
            
        except Exception as e:
            logger.error(f"人口予測エラー: {e}")
            raise
    
    def _apply_policy_effects(self, prediction_result: Dict, policy_scenario: Dict) -> Dict:
        """
        政策効果を予測結果に反映
        
        Args:
            prediction_result: 基本予測結果
            policy_scenario: 政策シナリオ
            
        Returns:
            政策効果を反映した予測結果
        """
        try:
            # 政策効果の係数（例：子育て支援政策で出生率+10%、移住支援で転入+5%等）
            policy_effects = {
                'childcare_support': 0.1,  # 子育て支援
                'migration_support': 0.05,  # 移住支援
                'economic_development': 0.03,  # 経済活性化
                'senior_support': -0.02  # 高齢者支援（直接的な人口増加効果は限定的）
            }
            
            # 政策効果を累積的に適用
            total_effect = 1.0
            for policy, intensity in policy_scenario.items():
                if policy in policy_effects:
                    effect = policy_effects[policy] * intensity  # 政策強度（0-1）を乗算
                    total_effect += effect
            
            # 予測値に効果を適用
            adjusted_forecast = [value * total_effect for value in prediction_result['forecast']]
            prediction_result['forecast_adjusted'] = adjusted_forecast
            prediction_result['policy_effect_factor'] = total_effect
            
            logger.info(f"政策効果適用完了: 効果係数={total_effect:.3f}")
            return prediction_result
            
        except Exception as e:
            logger.error(f"政策効果適用エラー: {e}")
            raise
    
    def ensemble_predict(self, years_ahead: int = 10, 
                        policy_scenario: Optional[Dict] = None) -> Dict:
        """
        アンサンブル予測（複数モデルの結果を統合）
        
        Args:
            years_ahead: 予測期間
            policy_scenario: 政策シナリオ
            
        Returns:
            アンサンブル予測結果
        """
        try:
            logger.info("アンサンブル予測開始")
            
            predictions = {}
            weights = {'arima': 0.3, 'xgboost': 0.4, 'random_forest': 0.3}
            
            # 各モデルから予測取得
            for model_type in ['arima', 'xgboost', 'random_forest']:
                if model_type in self.models:
                    pred = self.predict_population(model_type, years_ahead, policy_scenario)
                    predictions[model_type] = pred
            
            # 重み付き平均でアンサンブル
            if predictions:
                ensemble_forecast = np.zeros(years_ahead)
                for model_type, pred in predictions.items():
                    weight = weights.get(model_type, 1.0 / len(predictions))
                    forecast = pred.get('forecast_adjusted', pred['forecast'])
                    ensemble_forecast += np.array(forecast[:years_ahead]) * weight
                
                result = {
                    'forecast': ensemble_forecast,
                    'individual_predictions': predictions,
                    'weights': weights,
                    'dates': pd.date_range(start=datetime.now(), periods=years_ahead, freq='Y')
                }
                
                logger.info("アンサンブル予測完了")
                return result
            else:
                raise ValueError("利用可能な学習済みモデルがありません")
                
        except Exception as e:
            logger.error(f"アンサンブル予測エラー: {e}")
            raise
    
    def evaluate_models(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        モデル性能評価
        
        Args:
            X: 特徴量データフレーム
            y: 目的変数シリーズ
            
        Returns:
            モデル別評価結果
        """
        try:
            evaluation_results = {}
            
            # 時系列分割
            tscv = TimeSeriesSplit(n_splits=5)
            
            for model_name, model in self.models.items():
                if model_name == 'arima':
                    # ARIMAは別途評価
                    continue
                
                cv_scores = {'mae': [], 'rmse': [], 'r2': []}
                
                for train_idx, test_idx in tscv.split(X):
                    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                    
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    
                    cv_scores['mae'].append(mean_absolute_error(y_test, y_pred))
                    cv_scores['rmse'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
                    cv_scores['r2'].append(r2_score(y_test, y_pred))
                
                evaluation_results[model_name] = {
                    'mae_mean': np.mean(cv_scores['mae']),
                    'mae_std': np.std(cv_scores['mae']),
                    'rmse_mean': np.mean(cv_scores['rmse']),
                    'rmse_std': np.std(cv_scores['rmse']),
                    'r2_mean': np.mean(cv_scores['r2']),
                    'r2_std': np.std(cv_scores['r2'])
                }
            
            logger.info("モデル評価完了")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"モデル評価エラー: {e}")
            raise
    
    def save_models(self) -> None:
        """学習済みモデルの保存"""
        try:
            import os
            os.makedirs(self.model_dir, exist_ok=True)
            
            for model_name, model in self.models.items():
                file_path = f"{self.model_dir}/population_{model_name}_model.pkl"
                joblib.dump(model, file_path)
                logger.info(f"モデル保存完了: {file_path}")
                
        except Exception as e:
            logger.error(f"モデル保存エラー: {e}")
            raise
    
    def load_models(self) -> None:
        """保存済みモデルの読み込み"""
        try:
            import os
            if not os.path.exists(self.model_dir):
                logger.warning("モデルディレクトリが見つかりません")
                return
            
            for file_name in os.listdir(self.model_dir):
                if file_name.startswith("population_") and file_name.endswith("_model.pkl"):
                    model_name = file_name.replace("population_", "").replace("_model.pkl", "")
                    file_path = os.path.join(self.model_dir, file_name)
                    self.models[model_name] = joblib.load(file_path)
                    logger.info(f"モデル読み込み完了: {model_name}")
                    
        except Exception as e:
            logger.error(f"モデル読み込みエラー: {e}")
            raise