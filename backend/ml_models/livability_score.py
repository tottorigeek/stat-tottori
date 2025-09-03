import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib

logger = logging.getLogger(__name__)

class LivabilityScorePredictor:
    """住みやすさスコア予測モデルクラス"""
    
    def __init__(self, model_dir: str = "backend/data/models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        
        # 住みやすさ指標の重み設定
        self.indicator_weights = {
            'education': 0.15,      # 教育環境
            'healthcare': 0.18,     # 医療・福祉
            'transportation': 0.12, # 交通利便性
            'economy': 0.15,        # 経済・雇用
            'environment': 0.10,    # 自然環境
            'safety': 0.08,         # 安全性
            'culture': 0.07,        # 文化・娯楽
            'housing': 0.15         # 住環境
        }
        
        # 指標別詳細項目と重み
        self.detailed_indicators = {
            'education': {
                'school_access': 0.4,        # 学校アクセス
                'education_quality': 0.3,    # 教育の質
                'child_support': 0.3         # 子育て支援
            },
            'healthcare': {
                'hospital_access': 0.4,      # 病院アクセス
                'medical_quality': 0.3,      # 医療の質
                'elder_care': 0.3           # 高齢者ケア
            },
            'transportation': {
                'public_transport': 0.5,     # 公共交通
                'road_access': 0.3,         # 道路状況
                'commute_time': 0.2         # 通勤時間
            },
            'economy': {
                'employment_rate': 0.4,      # 就業率
                'income_level': 0.3,         # 所得水準
                'business_environment': 0.3  # 事業環境
            },
            'environment': {
                'air_quality': 0.3,          # 大気質
                'green_space': 0.4,          # 緑地面積
                'noise_level': 0.3           # 騒音レベル
            },
            'safety': {
                'crime_rate': 0.6,           # 犯罪率
                'disaster_risk': 0.4         # 災害リスク
            },
            'culture': {
                'cultural_facilities': 0.5,  # 文化施設
                'recreation': 0.5            # レクリエーション
            },
            'housing': {
                'housing_cost': 0.4,         # 住居費
                'housing_quality': 0.3,      # 住環境品質
                'land_price': 0.3           # 地価
            }
        }
    
    def calculate_livability_score(self, indicators_data: Dict[str, Dict[str, float]]) -> Dict:
        """
        住みやすさスコア計算
        
        Args:
            indicators_data: 指標データ（カテゴリ別・項目別数値）
            
        Returns:
            住みやすさスコア結果
        """
        try:
            logger.info("住みやすさスコア計算開始")
            
            category_scores = {}
            detailed_breakdown = {}
            
            # カテゴリ別スコア計算
            for category, weight in self.indicator_weights.items():
                if category in indicators_data:
                    category_data = indicators_data[category]
                    detailed_weights = self.detailed_indicators.get(category, {})
                    
                    # 詳細項目のスコア計算
                    category_score = 0
                    item_scores = {}
                    
                    for item, value in category_data.items():
                        # 0-100スケールに正規化
                        normalized_value = self._normalize_indicator_value(item, value, category)
                        item_weight = detailed_weights.get(item, 1.0 / len(category_data))
                        
                        item_score = normalized_value * item_weight
                        category_score += item_score
                        item_scores[item] = {
                            'raw_value': value,
                            'normalized_value': normalized_value,
                            'weight': item_weight,
                            'weighted_score': item_score
                        }
                    
                    category_scores[category] = category_score
                    detailed_breakdown[category] = item_scores
            
            # 総合スコア計算
            total_score = sum(
                category_scores.get(category, 0) * weight 
                for category, weight in self.indicator_weights.items()
            )
            
            # スコアを100点満点に調整
            final_score = min(100, max(0, total_score))
            
            # ランク判定
            rank = self._determine_livability_rank(final_score)
            
            result = {
                'total_score': final_score,
                'rank': rank,
                'category_scores': category_scores,
                'detailed_breakdown': detailed_breakdown,
                'strengths': self._identify_strengths(category_scores),
                'improvement_areas': self._identify_improvement_areas(category_scores)
            }
            
            logger.info(f"住みやすさスコア計算完了: {final_score:.2f}点 (ランク: {rank})")
            return result
            
        except Exception as e:
            logger.error(f"住みやすさスコア計算エラー: {e}")
            raise
    
    def _normalize_indicator_value(self, indicator: str, value: float, category: str) -> float:
        """
        指標値を0-100スケールに正規化
        
        Args:
            indicator: 指標名
            value: 指標値
            category: カテゴリ
            
        Returns:
            正規化された値
        """
        # 指標別の正規化ルール（実際のデータ分布に基づいて調整が必要）
        normalization_rules = {
            'school_access': {'min': 0, 'max': 5, 'reverse': False},
            'hospital_access': {'min': 0, 'max': 10, 'reverse': False},
            'employment_rate': {'min': 40, 'max': 80, 'reverse': False},
            'crime_rate': {'min': 0, 'max': 10, 'reverse': True},
            'commute_time': {'min': 5, 'max': 60, 'reverse': True},
            'housing_cost': {'min': 30000, 'max': 150000, 'reverse': True},
            'air_quality': {'min': 0, 'max': 100, 'reverse': False},
            'green_space': {'min': 0, 'max': 100, 'reverse': False}
        }
        
        if indicator in normalization_rules:
            rule = normalization_rules[indicator]
            min_val, max_val = rule['min'], rule['max']
            
            # Min-Max正規化
            normalized = (value - min_val) / (max_val - min_val) * 100
            
            # 逆転指標の場合（値が小さいほど良い）
            if rule['reverse']:
                normalized = 100 - normalized
            
            # 0-100の範囲にクリップ
            normalized = max(0, min(100, normalized))
        else:
            # デフォルト正規化（値をそのまま使用、0-100にクリップ）
            normalized = max(0, min(100, value))
        
        return normalized
    
    def _determine_livability_rank(self, score: float) -> str:
        """スコアからランク判定"""
        if score >= 80:
            return "S (非常に住みやすい)"
        elif score >= 70:
            return "A (住みやすい)"
        elif score >= 60:
            return "B (やや住みやすい)"
        elif score >= 50:
            return "C (普通)"
        elif score >= 40:
            return "D (やや課題あり)"
        else:
            return "E (改善要)"
    
    def _identify_strengths(self, category_scores: Dict[str, float]) -> List[str]:
        """強み分野の特定"""
        avg_score = np.mean(list(category_scores.values()))
        strengths = [
            category for category, score in category_scores.items() 
            if score > avg_score * 1.1
        ]
        return strengths
    
    def _identify_improvement_areas(self, category_scores: Dict[str, float]) -> List[str]:
        """改善要分野の特定"""
        avg_score = np.mean(list(category_scores.values()))
        improvement_areas = [
            category for category, score in category_scores.items() 
            if score < avg_score * 0.9
        ]
        return improvement_areas
    
    def predict_score_changes(self, 
                            current_indicators: Dict[str, Dict[str, float]],
                            policy_effects: Dict[str, Dict[str, float]]) -> Dict:
        """
        政策実施による住みやすさスコア変化予測
        
        Args:
            current_indicators: 現在の指標値
            policy_effects: 政策による指標への効果
            
        Returns:
            スコア変化予測結果
        """
        try:
            logger.info("住みやすさスコア変化予測開始")
            
            # 現在のスコア計算
            current_result = self.calculate_livability_score(current_indicators)
            
            # 政策実施後の指標値を計算
            future_indicators = {}
            for category, indicators in current_indicators.items():
                future_indicators[category] = {}
                for indicator, current_value in indicators.items():
                    # 政策効果を加味
                    effect = policy_effects.get(category, {}).get(indicator, 0)
                    future_value = current_value + effect
                    future_indicators[category][indicator] = future_value
            
            # 将来のスコア計算
            future_result = self.calculate_livability_score(future_indicators)
            
            # 変化量計算
            score_change = future_result['total_score'] - current_result['total_score']
            rank_change = future_result['rank'] != current_result['rank']
            
            # カテゴリ別変化量
            category_changes = {}
            for category in current_result['category_scores']:
                current_score = current_result['category_scores'].get(category, 0)
                future_score = future_result['category_scores'].get(category, 0)
                category_changes[category] = future_score - current_score
            
            result = {
                'current_score': current_result['total_score'],
                'future_score': future_result['total_score'],
                'score_change': score_change,
                'current_rank': current_result['rank'],
                'future_rank': future_result['rank'],
                'rank_changed': rank_change,
                'category_changes': category_changes,
                'most_improved_categories': sorted(
                    category_changes.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3],
                'policy_effectiveness': self._evaluate_policy_effectiveness(category_changes, policy_effects)
            }
            
            logger.info(f"スコア変化予測完了: {score_change:+.2f}点変化")
            return result
            
        except Exception as e:
            logger.error(f"スコア変化予測エラー: {e}")
            raise
    
    def _evaluate_policy_effectiveness(self, 
                                     category_changes: Dict[str, float],
                                     policy_effects: Dict[str, Dict[str, float]]) -> Dict:
        """政策効果の評価"""
        policy_evaluation = {}
        
        for category, change in category_changes.items():
            if category in policy_effects and policy_effects[category]:
                # 政策投入量（効果の合計）
                total_policy_input = sum(policy_effects[category].values())
                
                # 効果効率（変化量/投入量）
                if total_policy_input > 0:
                    efficiency = change / total_policy_input
                    policy_evaluation[category] = {
                        'score_change': change,
                        'policy_input': total_policy_input,
                        'efficiency': efficiency,
                        'effectiveness_level': self._classify_effectiveness(efficiency)
                    }
        
        return policy_evaluation
    
    def _classify_effectiveness(self, efficiency: float) -> str:
        """効果効率の分類"""
        if efficiency >= 2.0:
            return "非常に効果的"
        elif efficiency >= 1.0:
            return "効果的"
        elif efficiency >= 0.5:
            return "やや効果的"
        else:
            return "効果限定的"
    
    def train_prediction_model(self, 
                             historical_data: pd.DataFrame,
                             target_column: str = 'livability_score') -> Dict:
        """
        住みやすさスコア予測モデルの学習
        
        Args:
            historical_data: 過去データ
            target_column: 目的変数列名
            
        Returns:
            学習結果
        """
        try:
            logger.info("住みやすさ予測モデル学習開始")
            
            # 特徴量とターゲットを分離
            feature_columns = [col for col in historical_data.columns if col != target_column]
            X = historical_data[feature_columns]
            y = historical_data[target_column]
            
            # データ前処理
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 学習・テスト分割
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # 複数モデルで学習
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
            }
            
            results = {}
            
            for model_name, model in models.items():
                # モデル学習
                model.fit(X_train, y_train)
                
                # 予測・評価
                y_pred = model.predict(X_test)
                
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                # 特徴量重要度
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(feature_columns, model.feature_importances_))
                else:
                    feature_importance = {}
                
                results[model_name] = {
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'feature_importance': feature_importance
                }
                
                # モデル保存
                self.models[model_name] = model
            
            # スケーラー保存
            self.scalers['livability_scaler'] = scaler
            
            logger.info("住みやすさ予測モデル学習完了")
            return results
            
        except Exception as e:
            logger.error(f"予測モデル学習エラー: {e}")
            raise
    
    def compare_municipalities(self, 
                             municipalities_data: Dict[str, Dict[str, Dict[str, float]]]) -> Dict:
        """
        市町村間の住みやすさ比較
        
        Args:
            municipalities_data: 市町村別指標データ
            
        Returns:
            比較結果
        """
        try:
            logger.info("市町村比較分析開始")
            
            comparison_results = {}
            
            # 各市町村のスコア計算
            for municipality, indicators in municipalities_data.items():
                score_result = self.calculate_livability_score(indicators)
                comparison_results[municipality] = score_result
            
            # ランキング作成
            rankings = sorted(
                comparison_results.items(),
                key=lambda x: x[1]['total_score'],
                reverse=True
            )
            
            # 統計情報
            scores = [result['total_score'] for result in comparison_results.values()]
            statistics = {
                'average_score': np.mean(scores),
                'median_score': np.median(scores),
                'std_score': np.std(scores),
                'max_score': np.max(scores),
                'min_score': np.min(scores)
            }
            
            # カテゴリ別ベスト市町村
            category_leaders = {}
            for category in self.indicator_weights.keys():
                best_municipality = max(
                    comparison_results.items(),
                    key=lambda x: x[1]['category_scores'].get(category, 0)
                )
                category_leaders[category] = {
                    'municipality': best_municipality[0],
                    'score': best_municipality[1]['category_scores'].get(category, 0)
                }
            
            result = {
                'rankings': rankings,
                'statistics': statistics,
                'category_leaders': category_leaders,
                'comparison_matrix': comparison_results
            }
            
            logger.info(f"市町村比較完了: {len(municipalities_data)}市町村")
            return result
            
        except Exception as e:
            logger.error(f"市町村比較エラー: {e}")
            raise
    
    def save_models(self) -> None:
        """モデル・設定の保存"""
        try:
            import os
            os.makedirs(self.model_dir, exist_ok=True)
            
            # 予測モデル保存
            for model_name, model in self.models.items():
                file_path = f"{self.model_dir}/livability_{model_name}_model.pkl"
                joblib.dump(model, file_path)
            
            # スケーラー保存
            for scaler_name, scaler in self.scalers.items():
                file_path = f"{self.model_dir}/livability_{scaler_name}.pkl"
                joblib.dump(scaler, file_path)
            
            # 設定データ保存
            config_data = {
                'indicator_weights': self.indicator_weights,
                'detailed_indicators': self.detailed_indicators
            }
            
            config_path = f"{self.model_dir}/livability_config.pkl"
            joblib.dump(config_data, config_path)
            
            logger.info("住みやすさモデル保存完了")
            
        except Exception as e:
            logger.error(f"モデル保存エラー: {e}")
            raise