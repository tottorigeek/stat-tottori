import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class EconomicImpactPredictor:
    """経済効果予測モデルクラス"""
    
    def __init__(self, model_dir: str = "backend/data/models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        
        # 産業連関表データ（簡略化版）
        self.input_output_matrix = self._create_sample_io_matrix()
        
        # 経済指標の相関関係
        self.economic_relationships = {
            'population_gdp_elasticity': 0.8,  # 人口とGDPの弾性値
            'employment_gdp_ratio': 0.6,       # 雇用とGDPの比率
            'investment_multiplier': 1.5,      # 投資乗数
            'consumption_propensity': 0.7      # 消費性向
        }
    
    def _create_sample_io_matrix(self) -> np.ndarray:
        """
        産業連関表のサンプルデータ作成
        
        Returns:
            産業連関係数行列
        """
        # 簡略化された産業分類（農業、製造業、サービス業）
        industries = ['agriculture', 'manufacturing', 'services']
        n = len(industries)
        
        # サンプル産業連関係数
        io_matrix = np.array([
            [0.1, 0.05, 0.02],  # 農業
            [0.15, 0.25, 0.1],   # 製造業
            [0.05, 0.2, 0.3]     # サービス業
        ])
        
        return io_matrix
    
    def calculate_economic_impact(self, 
                                policy_investment: Dict[str, float],
                                direct_effects: Dict[str, float]) -> Dict:
        """
        政策投資による経済波及効果計算
        
        Args:
            policy_investment: 政策別投資額（億円）
            direct_effects: 直接効果（雇用創出等）
            
        Returns:
            経済波及効果の詳細結果
        """
        try:
            logger.info("経済波及効果計算開始")
            
            # 1. 直接効果
            total_investment = sum(policy_investment.values())
            direct_gdp_impact = total_investment * 0.6  # 投資額の60%がGDPに直接寄与
            
            # 2. 1次間接効果（産業連関分析）
            # 投資を産業別に配分
            industry_investment = self._allocate_investment_by_industry(policy_investment)
            
            # 産業連関による1次波及効果
            primary_effects = np.dot(self.input_output_matrix, industry_investment)
            primary_gdp_impact = np.sum(primary_effects)
            
            # 3. 2次間接効果（消費増加による効果）
            # 雇用創出による所得増加
            employment_increase = direct_effects.get('employment_increase', 0)
            average_income = 300  # 平均年収300万円（仮定）
            income_increase = employment_increase * average_income / 10000  # 億円単位
            
            # 消費増加による2次効果
            secondary_gdp_impact = income_increase * self.economic_relationships['consumption_propensity'] * 1.2
            
            # 4. 総合経済効果
            total_gdp_impact = direct_gdp_impact + primary_gdp_impact + secondary_gdp_impact
            
            # 5. 雇用効果計算
            gdp_employment_ratio = 0.8  # GDP1億円あたり0.8人雇用創出（仮定）
            total_employment_impact = total_gdp_impact * gdp_employment_ratio
            
            # 6. 税収効果
            tax_rate = 0.15  # 実効税率15%（仮定）
            tax_revenue_impact = total_gdp_impact * tax_rate
            
            result = {
                'total_investment': total_investment,
                'direct_gdp_impact': direct_gdp_impact,
                'primary_gdp_impact': primary_gdp_impact,
                'secondary_gdp_impact': secondary_gdp_impact,
                'total_gdp_impact': total_gdp_impact,
                'employment_impact': total_employment_impact,
                'tax_revenue_impact': tax_revenue_impact,
                'multiplier_effect': total_gdp_impact / total_investment if total_investment > 0 else 0,
                'industry_breakdown': {
                    'agriculture': primary_effects[0],
                    'manufacturing': primary_effects[1],
                    'services': primary_effects[2]
                }
            }
            
            logger.info(f"経済波及効果計算完了: 総効果={total_gdp_impact:.2f}億円")
            return result
            
        except Exception as e:
            logger.error(f"経済波及効果計算エラー: {e}")
            raise
    
    def _allocate_investment_by_industry(self, policy_investment: Dict[str, float]) -> np.ndarray:
        """
        政策投資を産業別に配分
        
        Args:
            policy_investment: 政策別投資額
            
        Returns:
            産業別投資配分
        """
        # 政策と産業の対応関係（簡略化）
        policy_industry_mapping = {
            'childcare_support': [0.1, 0.2, 0.7],     # 子育て支援 → 主にサービス業
            'migration_support': [0.05, 0.3, 0.65],   # 移住支援 → 製造業・サービス業
            'agriculture_support': [0.8, 0.1, 0.1],   # 農業支援 → 主に農業
            'manufacturing_support': [0.1, 0.7, 0.2], # 製造業支援 → 主に製造業
            'tourism_promotion': [0.1, 0.1, 0.8],     # 観光振興 → 主にサービス業
            'infrastructure': [0.1, 0.6, 0.3]         # インフラ → 主に製造業
        }
        
        # 産業別投資額を計算
        industry_investment = np.zeros(3)  # 3産業
        
        for policy, amount in policy_investment.items():
            if policy in policy_industry_mapping:
                allocation = np.array(policy_industry_mapping[policy])
                industry_investment += allocation * amount
            else:
                # デフォルト配分（均等配分）
                industry_investment += np.array([0.33, 0.33, 0.34]) * amount
        
        return industry_investment
    
    def predict_gdp_impact(self, 
                          population_change: float,
                          employment_change: float,
                          investment_amount: float,
                          years_ahead: int = 5) -> Dict:
        """
        GDP影響予測
        
        Args:
            population_change: 人口変化率
            employment_change: 雇用変化率
            investment_amount: 投資額（億円）
            years_ahead: 予測期間（年）
            
        Returns:
            GDP影響予測結果
        """
        try:
            logger.info("GDP影響予測開始")
            
            # 基準GDP（鳥取県のGDP約1.8兆円を仮定）
            base_gdp = 18000  # 億円
            
            gdp_projections = []
            
            for year in range(1, years_ahead + 1):
                # 人口効果
                population_effect = base_gdp * population_change * self.economic_relationships['population_gdp_elasticity'] * year
                
                # 雇用効果
                employment_effect = base_gdp * employment_change * self.economic_relationships['employment_gdp_ratio'] * year
                
                # 投資効果（逓減効果を考慮）
                investment_effect = investment_amount * self.economic_relationships['investment_multiplier'] * (0.9 ** (year - 1))
                
                # 年間GDP予測
                annual_gdp = base_gdp + population_effect + employment_effect + investment_effect
                gdp_projections.append(annual_gdp)
            
            # 累積効果
            cumulative_impact = sum(gdp_projections) - base_gdp * years_ahead
            
            result = {
                'base_gdp': base_gdp,
                'annual_projections': gdp_projections,
                'cumulative_impact': cumulative_impact,
                'average_annual_growth': (gdp_projections[-1] - base_gdp) / base_gdp * 100,
                'years': list(range(1, years_ahead + 1))
            }
            
            logger.info(f"GDP影響予測完了: 累積効果={cumulative_impact:.2f}億円")
            return result
            
        except Exception as e:
            logger.error(f"GDP影響予測エラー: {e}")
            raise
    
    def predict_employment_impact(self, 
                                 policy_scenario: Dict[str, float],
                                 years_ahead: int = 5) -> Dict:
        """
        雇用創出効果予測
        
        Args:
            policy_scenario: 政策シナリオ
            years_ahead: 予測期間
            
        Returns:
            雇用影響予測結果
        """
        try:
            logger.info("雇用創出効果予測開始")
            
            # 政策別雇用創出効果（投資1億円あたりの雇用創出数）
            employment_coefficients = {
                'childcare_support': 2.5,      # 保育士等の直接雇用
                'migration_support': 1.2,      # 移住促進による間接雇用
                'agriculture_support': 1.8,    # 農業従事者増加
                'manufacturing_support': 2.0,  # 製造業雇用
                'tourism_promotion': 2.2,      # 観光業雇用
                'infrastructure': 1.5          # 建設業雇用
            }
            
            employment_projections = []
            
            for year in range(1, years_ahead + 1):
                annual_employment = 0
                
                for policy, investment in policy_scenario.items():
                    if policy in employment_coefficients:
                        coeff = employment_coefficients[policy]
                        # 時間経過による効果の変化を考慮
                        time_factor = min(1.0, year * 0.3)  # 3年で最大効果
                        annual_employment += investment * coeff * time_factor
                
                employment_projections.append(annual_employment)
            
            # 産業別内訳
            industry_breakdown = self._calculate_employment_by_industry(policy_scenario)
            
            result = {
                'annual_employment_creation': employment_projections,
                'total_employment_creation': sum(employment_projections),
                'industry_breakdown': industry_breakdown,
                'years': list(range(1, years_ahead + 1))
            }
            
            logger.info(f"雇用創出効果予測完了: 総雇用創出={sum(employment_projections):.0f}人")
            return result
            
        except Exception as e:
            logger.error(f"雇用創出効果予測エラー: {e}")
            raise
    
    def _calculate_employment_by_industry(self, policy_scenario: Dict[str, float]) -> Dict:
        """産業別雇用効果計算"""
        industry_employment = {
            'agriculture': 0,
            'manufacturing': 0,
            'services': 0
        }
        
        # 政策と産業の雇用効果マッピング
        policy_industry_employment = {
            'childcare_support': {'services': 0.9, 'manufacturing': 0.05, 'agriculture': 0.05},
            'agriculture_support': {'agriculture': 0.8, 'manufacturing': 0.1, 'services': 0.1},
            'manufacturing_support': {'manufacturing': 0.7, 'services': 0.2, 'agriculture': 0.1},
            'tourism_promotion': {'services': 0.8, 'manufacturing': 0.1, 'agriculture': 0.1}
        }
        
        for policy, investment in policy_scenario.items():
            if policy in policy_industry_employment:
                for industry, ratio in policy_industry_employment[policy].items():
                    industry_employment[industry] += investment * 2.0 * ratio  # 平均雇用係数2.0
        
        return industry_employment
    
    def predict_tax_revenue(self, 
                           gdp_impact: float,
                           employment_impact: float,
                           years_ahead: int = 5) -> Dict:
        """
        税収影響予測
        
        Args:
            gdp_impact: GDP影響額（億円）
            employment_impact: 雇用創出数（人）
            years_ahead: 予測期間
            
        Returns:
            税収影響予測結果
        """
        try:
            logger.info("税収影響予測開始")
            
            # 税収係数
            tax_coefficients = {
                'corporate_tax_rate': 0.23,    # 法人税率
                'income_tax_rate': 0.10,       # 所得税率（実効）
                'consumption_tax_rate': 0.08,  # 消費税率（実効）
                'local_tax_rate': 0.05         # 地方税率
            }
            
            annual_tax_revenue = []
            
            for year in range(1, years_ahead + 1):
                # 法人税収増（GDP増加による）
                corporate_tax = gdp_impact * tax_coefficients['corporate_tax_rate'] * 0.3  # 30%が企業利益
                
                # 所得税収増（雇用増加による）
                average_income = 300  # 万円
                income_tax = employment_impact * average_income * tax_coefficients['income_tax_rate'] / 10000  # 億円
                
                # 消費税収増
                consumption_tax = gdp_impact * tax_coefficients['consumption_tax_rate'] * 0.6  # 60%が消費
                
                # 地方税収増
                local_tax = gdp_impact * tax_coefficients['local_tax_rate']
                
                total_annual_tax = corporate_tax + income_tax + consumption_tax + local_tax
                annual_tax_revenue.append(total_annual_tax)
            
            result = {
                'annual_tax_revenue': annual_tax_revenue,
                'total_tax_revenue': sum(annual_tax_revenue),
                'tax_breakdown': {
                    'corporate_tax': corporate_tax,
                    'income_tax': income_tax,
                    'consumption_tax': consumption_tax,
                    'local_tax': local_tax
                },
                'years': list(range(1, years_ahead + 1))
            }
            
            logger.info(f"税収影響予測完了: 総税収増={sum(annual_tax_revenue):.2f}億円")
            return result
            
        except Exception as e:
            logger.error(f"税収影響予測エラー: {e}")
            raise
    
    def comprehensive_economic_analysis(self, 
                                      policy_scenario: Dict[str, float],
                                      population_change: float = 0,
                                      years_ahead: int = 5) -> Dict:
        """
        包括的経済分析
        
        Args:
            policy_scenario: 政策シナリオ（政策別投資額）
            population_change: 人口変化率
            years_ahead: 予測期間
            
        Returns:
            包括的経済分析結果
        """
        try:
            logger.info("包括的経済分析開始")
            
            # 1. 経済波及効果分析
            direct_effects = {'employment_increase': sum(policy_scenario.values()) * 2}  # 投資額に比例する雇用効果
            economic_impact = self.calculate_economic_impact(policy_scenario, direct_effects)
            
            # 2. GDP影響予測
            total_investment = sum(policy_scenario.values())
            employment_change = economic_impact['employment_impact'] / 300000 * 100  # 雇用変化率（％）
            gdp_prediction = self.predict_gdp_impact(population_change, employment_change, total_investment, years_ahead)
            
            # 3. 雇用影響予測
            employment_prediction = self.predict_employment_impact(policy_scenario, years_ahead)
            
            # 4. 税収影響予測
            tax_prediction = self.predict_tax_revenue(
                economic_impact['total_gdp_impact'],
                economic_impact['employment_impact'],
                years_ahead
            )
            
            # 5. ROI（投資収益率）計算
            total_benefits = gdp_prediction['cumulative_impact'] + tax_prediction['total_tax_revenue']
            roi = (total_benefits - total_investment) / total_investment * 100 if total_investment > 0 else 0
            
            # 6. 結果統合
            comprehensive_result = {
                'policy_scenario': policy_scenario,
                'total_investment': total_investment,
                'economic_impact': economic_impact,
                'gdp_prediction': gdp_prediction,
                'employment_prediction': employment_prediction,
                'tax_prediction': tax_prediction,
                'roi_percent': roi,
                'payback_period': total_investment / (tax_prediction['total_tax_revenue'] / years_ahead) if tax_prediction['total_tax_revenue'] > 0 else float('inf'),
                'summary': {
                    'total_gdp_impact': economic_impact['total_gdp_impact'],
                    'total_employment_creation': employment_prediction['total_employment_creation'],
                    'total_tax_revenue': tax_prediction['total_tax_revenue'],
                    'multiplier_effect': economic_impact['multiplier_effect']
                }
            }
            
            logger.info(f"包括的経済分析完了: ROI={roi:.2f}%")
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"包括的経済分析エラー: {e}")
            raise
    
    def save_models(self) -> None:
        """モデル保存"""
        try:
            import os
            os.makedirs(self.model_dir, exist_ok=True)
            
            # 産業連関表と経済係数を保存
            economic_data = {
                'input_output_matrix': self.input_output_matrix,
                'economic_relationships': self.economic_relationships
            }
            
            file_path = f"{self.model_dir}/economic_impact_data.pkl"
            joblib.dump(economic_data, file_path)
            
            logger.info("経済分析データ保存完了")
            
        except Exception as e:
            logger.error(f"モデル保存エラー: {e}")
            raise