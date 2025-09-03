import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from datetime import datetime
import cvxpy as cp
from scipy.optimize import minimize, differential_evolution
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import joblib

logger = logging.getLogger(__name__)

class PolicyOptimizer:
    """政策最適化アルゴリズムクラス"""
    
    def __init__(self, 
                 population_model=None, 
                 economic_model=None, 
                 livability_model=None):
        self.population_model = population_model
        self.economic_model = economic_model
        self.livability_model = livability_model
        
        # 政策種別と効果パラメータ
        self.policy_types = {
            'childcare_support': {
                'cost_per_unit': 0.5,        # 億円/単位強度
                'population_effect': 0.02,   # 人口への効果係数
                'economic_effect': 0.015,    # 経済への効果係数
                'livability_effect': 0.03,   # 住みやすさへの効果係数
                'max_intensity': 10,         # 最大強度
                'implementation_time': 2     # 実装期間（年）
            },
            'migration_support': {
                'cost_per_unit': 0.3,
                'population_effect': 0.03,
                'economic_effect': 0.02,
                'livability_effect': 0.02,
                'max_intensity': 8,
                'implementation_time': 1
            },
            'economic_development': {
                'cost_per_unit': 1.0,
                'population_effect': 0.015,
                'economic_effect': 0.04,
                'livability_effect': 0.025,
                'max_intensity': 15,
                'implementation_time': 3
            },
            'infrastructure_improvement': {
                'cost_per_unit': 2.0,
                'population_effect': 0.01,
                'economic_effect': 0.03,
                'livability_effect': 0.04,
                'max_intensity': 20,
                'implementation_time': 5
            },
            'education_enhancement': {
                'cost_per_unit': 0.8,
                'population_effect': 0.025,
                'economic_effect': 0.02,
                'livability_effect': 0.035,
                'max_intensity': 12,
                'implementation_time': 4
            },
            'healthcare_improvement': {
                'cost_per_unit': 1.5,
                'population_effect': 0.02,
                'economic_effect': 0.015,
                'livability_effect': 0.05,
                'max_intensity': 10,
                'implementation_time': 3
            }
        }
        
        # 制約条件
        self.constraints = {
            'total_budget': 100.0,          # 総予算（億円）
            'annual_budget': 25.0,          # 年間予算上限
            'min_policy_intensity': 0.0,    # 最小政策強度
            'max_policies': 5,              # 同時実施可能政策数
            'implementation_capacity': 30   # 年間実装キャパシティ
        }
    
    def optimize_budget_allocation(self, 
                                 objective: str = "total_benefit",
                                 constraints: Optional[Dict] = None,
                                 optimization_method: str = "linear_programming") -> Dict:
        """
        予算配分最適化
        
        Args:
            objective: 最適化目的 ("total_benefit", "population_growth", "economic_impact", "livability_improvement")
            constraints: 制約条件
            optimization_method: 最適化手法 ("linear_programming", "genetic_algorithm", "bayesian_optimization")
            
        Returns:
            最適化結果
        """
        try:
            logger.info(f"{optimization_method}による予算配分最適化開始")
            
            # 制約条件更新
            if constraints:
                self.constraints.update(constraints)
            
            # 最適化手法選択
            if optimization_method == "linear_programming":
                result = self._linear_programming_optimization(objective)
            elif optimization_method == "genetic_algorithm":
                result = self._genetic_algorithm_optimization(objective)
            elif optimization_method == "bayesian_optimization":
                result = self._bayesian_optimization(objective)
            else:
                raise ValueError(f"未対応の最適化手法: {optimization_method}")
            
            # 結果の後処理・検証
            validated_result = self._validate_optimization_result(result)
            
            logger.info(f"予算配分最適化完了: 総効果={validated_result['total_objective_value']:.3f}")
            return validated_result
            
        except Exception as e:
            logger.error(f"予算配分最適化エラー: {e}")
            raise
    
    def _linear_programming_optimization(self, objective: str) -> Dict:
        """
        線形計画法による最適化
        
        Args:
            objective: 最適化目的
            
        Returns:
            最適化結果
        """
        try:
            policies = list(self.policy_types.keys())
            n_policies = len(policies)
            
            # 決定変数（政策強度）
            x = cp.Variable(n_policies, nonneg=True)
            
            # 目的関数係数
            objective_coeffs = self._get_objective_coefficients(objective, policies)
            objective_func = cp.Maximize(objective_coeffs @ x)
            
            # 制約条件
            constraints = []
            
            # 予算制約
            cost_coeffs = [self.policy_types[policy]['cost_per_unit'] for policy in policies]
            constraints.append(cost_coeffs @ x <= self.constraints['total_budget'])
            
            # 政策強度上限
            for i, policy in enumerate(policies):
                constraints.append(x[i] <= self.policy_types[policy]['max_intensity'])
            
            # 政策数制約（0-1変数で近似）
            # 実装を簡略化し、すべての政策が利用可能とする
            
            # 問題定義・求解
            problem = cp.Problem(objective_func, constraints)
            problem.solve()
            
            if problem.status not in ["infeasible", "unbounded"]:
                optimal_allocation = dict(zip(policies, x.value))
                
                # 結果計算
                total_cost = sum(
                    optimal_allocation[policy] * self.policy_types[policy]['cost_per_unit']
                    for policy in policies
                )
                
                # 効果計算
                effects = self._calculate_policy_effects(optimal_allocation)
                
                result = {
                    'optimal_allocation': optimal_allocation,
                    'total_cost': total_cost,
                    'total_objective_value': problem.value,
                    'optimization_status': problem.status,
                    'predicted_effects': effects,
                    'budget_utilization': total_cost / self.constraints['total_budget'] * 100
                }
                
                return result
            else:
                raise ValueError(f"最適化に失敗しました: {problem.status}")
                
        except Exception as e:
            logger.error(f"線形計画法最適化エラー: {e}")
            raise
    
    def _genetic_algorithm_optimization(self, objective: str) -> Dict:
        """
        遺伝アルゴリズムによる最適化
        
        Args:
            objective: 最適化目的
            
        Returns:
            最適化結果
        """
        try:
            policies = list(self.policy_types.keys())
            n_policies = len(policies)
            
            # 決定変数の境界（各政策の強度範囲）
            bounds = [
                (0, self.policy_types[policy]['max_intensity'])
                for policy in policies
            ]
            
            # 目的関数（最小化問題に変換）
            def objective_function(x):
                allocation = dict(zip(policies, x))
                
                # 制約違反ペナルティ
                penalty = 0
                
                # 予算制約
                total_cost = sum(
                    allocation[policy] * self.policy_types[policy]['cost_per_unit']
                    for policy in policies
                )
                if total_cost > self.constraints['total_budget']:
                    penalty += (total_cost - self.constraints['total_budget']) * 1000
                
                # 目的関数値計算
                effects = self._calculate_policy_effects(allocation)
                
                if objective == "total_benefit":
                    obj_value = effects['population_effect'] + effects['economic_effect'] + effects['livability_effect']
                elif objective == "population_growth":
                    obj_value = effects['population_effect']
                elif objective == "economic_impact":
                    obj_value = effects['economic_effect']
                elif objective == "livability_improvement":
                    obj_value = effects['livability_effect']
                
                # 最小化のため負の値を返す
                return -(obj_value - penalty)
            
            # 遺伝アルゴリズム実行
            result = differential_evolution(
                objective_function,
                bounds,
                maxiter=100,
                popsize=20,
                seed=42
            )
            
            if result.success:
                optimal_allocation = dict(zip(policies, result.x))
                
                total_cost = sum(
                    optimal_allocation[policy] * self.policy_types[policy]['cost_per_unit']
                    for policy in policies
                )
                
                effects = self._calculate_policy_effects(optimal_allocation)
                
                optimization_result = {
                    'optimal_allocation': optimal_allocation,
                    'total_cost': total_cost,
                    'total_objective_value': -result.fun,
                    'optimization_status': 'optimal',
                    'predicted_effects': effects,
                    'budget_utilization': total_cost / self.constraints['total_budget'] * 100
                }
                
                return optimization_result
            else:
                raise ValueError(f"遺伝アルゴリズム最適化に失敗: {result.message}")
                
        except Exception as e:
            logger.error(f"遺伝アルゴリズム最適化エラー: {e}")
            raise
    
    def _bayesian_optimization(self, objective: str) -> Dict:
        """
        ベイズ最適化
        
        Args:
            objective: 最適化目的
            
        Returns:
            最適化結果
        """
        try:
            # ベイズ最適化の簡略実装
            # 実際の実装では、scikit-optimizeやoptuna等を使用
            
            policies = list(self.policy_types.keys())
            n_iterations = 50
            
            # ガウス過程回帰モデル
            kernel = C(1.0) * RBF(1.0)
            gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-6)
            
            # 初期サンプリング
            n_initial = 10
            X_samples = []
            y_samples = []
            
            for _ in range(n_initial):
                # ランダムサンプリング
                sample = np.array([
                    np.random.uniform(0, self.policy_types[policy]['max_intensity'])
                    for policy in policies
                ])
                
                # 制約チェック・調整
                sample = self._adjust_sample_to_constraints(sample, policies)
                
                # 目的関数評価
                obj_value = self._evaluate_objective(sample, policies, objective)
                
                X_samples.append(sample)
                y_samples.append(obj_value)
            
            X_samples = np.array(X_samples)
            y_samples = np.array(y_samples)
            
            # ベイズ最適化イテレーション
            for i in range(n_iterations - n_initial):
                # ガウス過程学習
                gpr.fit(X_samples, y_samples)
                
                # 獲得関数（Upper Confidence Bound）による次候補選択
                next_sample = self._select_next_sample_ucb(gpr, policies)
                
                # 目的関数評価
                obj_value = self._evaluate_objective(next_sample, policies, objective)
                
                # サンプル追加
                X_samples = np.vstack([X_samples, next_sample])
                y_samples = np.append(y_samples, obj_value)
            
            # 最良解選択
            best_idx = np.argmax(y_samples)
            optimal_allocation = dict(zip(policies, X_samples[best_idx]))
            
            total_cost = sum(
                optimal_allocation[policy] * self.policy_types[policy]['cost_per_unit']
                for policy in policies
            )
            
            effects = self._calculate_policy_effects(optimal_allocation)
            
            result = {
                'optimal_allocation': optimal_allocation,
                'total_cost': total_cost,
                'total_objective_value': y_samples[best_idx],
                'optimization_status': 'optimal',
                'predicted_effects': effects,
                'budget_utilization': total_cost / self.constraints['total_budget'] * 100,
                'n_evaluations': len(y_samples)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"ベイズ最適化エラー: {e}")
            raise
    
    def _get_objective_coefficients(self, objective: str, policies: List[str]) -> np.ndarray:
        """目的関数の係数取得"""
        coeffs = np.zeros(len(policies))
        
        for i, policy in enumerate(policies):
            policy_params = self.policy_types[policy]
            
            if objective == "total_benefit":
                coeffs[i] = (policy_params['population_effect'] + 
                           policy_params['economic_effect'] + 
                           policy_params['livability_effect'])
            elif objective == "population_growth":
                coeffs[i] = policy_params['population_effect']
            elif objective == "economic_impact":
                coeffs[i] = policy_params['economic_effect']
            elif objective == "livability_improvement":
                coeffs[i] = policy_params['livability_effect']
        
        return coeffs
    
    def _calculate_policy_effects(self, allocation: Dict[str, float]) -> Dict:
        """政策効果計算"""
        total_population_effect = 0
        total_economic_effect = 0
        total_livability_effect = 0
        
        for policy, intensity in allocation.items():
            if policy in self.policy_types:
                params = self.policy_types[policy]
                total_population_effect += intensity * params['population_effect']
                total_economic_effect += intensity * params['economic_effect']
                total_livability_effect += intensity * params['livability_effect']
        
        return {
            'population_effect': total_population_effect,
            'economic_effect': total_economic_effect,
            'livability_effect': total_livability_effect
        }
    
    def _adjust_sample_to_constraints(self, sample: np.ndarray, policies: List[str]) -> np.ndarray:
        """制約条件に合わせてサンプルを調整"""
        # 予算制約を満たすように調整
        total_cost = sum(
            sample[i] * self.policy_types[policies[i]]['cost_per_unit']
            for i in range(len(policies))
        )
        
        if total_cost > self.constraints['total_budget']:
            # 比例縮小
            scale_factor = self.constraints['total_budget'] / total_cost
            sample = sample * scale_factor
        
        # 上限制約
        for i, policy in enumerate(policies):
            max_intensity = self.policy_types[policy]['max_intensity']
            sample[i] = min(sample[i], max_intensity)
        
        return sample
    
    def _evaluate_objective(self, sample: np.ndarray, policies: List[str], objective: str) -> float:
        """目的関数評価"""
        allocation = dict(zip(policies, sample))
        effects = self._calculate_policy_effects(allocation)
        
        if objective == "total_benefit":
            return effects['population_effect'] + effects['economic_effect'] + effects['livability_effect']
        elif objective == "population_growth":
            return effects['population_effect']
        elif objective == "economic_impact":
            return effects['economic_effect']
        elif objective == "livability_improvement":
            return effects['livability_effect']
    
    def _select_next_sample_ucb(self, gpr: GaussianProcessRegressor, policies: List[str]) -> np.ndarray:
        """Upper Confidence Boundによる次サンプル選択（簡略版）"""
        # 実際の実装では、より洗練された獲得関数を使用
        n_candidates = 1000
        candidates = []
        
        for _ in range(n_candidates):
            candidate = np.array([
                np.random.uniform(0, self.policy_types[policy]['max_intensity'])
                for policy in policies
            ])
            candidate = self._adjust_sample_to_constraints(candidate, policies)
            candidates.append(candidate)
        
        candidates = np.array(candidates)
        
        # UCB計算
        mean, std = gpr.predict(candidates, return_std=True)
        ucb = mean + 2.0 * std
        
        # 最大UCB値の候補を選択
        best_idx = np.argmax(ucb)
        return candidates[best_idx]
    
    def _validate_optimization_result(self, result: Dict) -> Dict:
        """最適化結果の検証"""
        allocation = result['optimal_allocation']
        
        # 制約条件チェック
        violations = []
        
        # 予算制約
        total_cost = result['total_cost']
        if total_cost > self.constraints['total_budget']:
            violations.append(f"予算制約違反: {total_cost:.2f} > {self.constraints['total_budget']}")
        
        # 政策強度上限
        for policy, intensity in allocation.items():
            max_intensity = self.policy_types[policy]['max_intensity']
            if intensity > max_intensity:
                violations.append(f"政策強度上限違反 {policy}: {intensity:.2f} > {max_intensity}")
        
        # 検証結果追加
        result['constraint_violations'] = violations
        result['is_feasible'] = len(violations) == 0
        
        # 効果予測の信頼区間計算（簡略版）
        effects = result['predicted_effects']
        uncertainty = {
            'population_effect_range': [effects['population_effect'] * 0.8, effects['population_effect'] * 1.2],
            'economic_effect_range': [effects['economic_effect'] * 0.7, effects['economic_effect'] * 1.3],
            'livability_effect_range': [effects['livability_effect'] * 0.9, effects['livability_effect'] * 1.1]
        }
        result['effect_uncertainty'] = uncertainty
        
        return result
    
    def optimize_policy_timing(self, 
                              policy_allocation: Dict[str, float],
                              time_horizon: int = 10) -> Dict:
        """
        政策実施タイミングの最適化
        
        Args:
            policy_allocation: 政策配分
            time_horizon: 計画期間（年）
            
        Returns:
            タイミング最適化結果
        """
        try:
            logger.info("政策実施タイミング最適化開始")
            
            implementation_schedule = {}
            total_annual_cost = np.zeros(time_horizon)
            
            # 政策を効果/コスト比でソート
            policy_efficiency = {}
            for policy, intensity in policy_allocation.items():
                if intensity > 0:
                    cost = intensity * self.policy_types[policy]['cost_per_unit']
                    effects = self._calculate_policy_effects({policy: intensity})
                    total_effect = sum(effects.values())
                    efficiency = total_effect / cost if cost > 0 else 0
                    policy_efficiency[policy] = efficiency
            
            sorted_policies = sorted(policy_efficiency.items(), key=lambda x: x[1], reverse=True)
            
            # 年間予算制約下でのスケジューリング
            for policy, efficiency in sorted_policies:
                intensity = policy_allocation[policy]
                implementation_time = self.policy_types[policy]['implementation_time']
                annual_cost = intensity * self.policy_types[policy]['cost_per_unit'] / implementation_time
                
                # 実施開始年を決定
                for start_year in range(time_horizon - implementation_time + 1):
                    # 期間中の予算制約チェック
                    can_implement = True
                    for year in range(start_year, start_year + implementation_time):
                        if total_annual_cost[year] + annual_cost > self.constraints['annual_budget']:
                            can_implement = False
                            break
                    
                    if can_implement:
                        # スケジュールに追加
                        implementation_schedule[policy] = {
                            'start_year': start_year,
                            'end_year': start_year + implementation_time - 1,
                            'annual_cost': annual_cost,
                            'total_cost': intensity * self.policy_types[policy]['cost_per_unit'],
                            'efficiency': efficiency
                        }
                        
                        # 年間コストを更新
                        for year in range(start_year, start_year + implementation_time):
                            total_annual_cost[year] += annual_cost
                        
                        break
            
            # 効果の時間推移計算
            annual_effects = np.zeros((time_horizon, 3))  # [population, economic, livability]
            
            for policy, schedule in implementation_schedule.items():
                intensity = policy_allocation[policy]
                params = self.policy_types[policy]
                
                for year in range(schedule['start_year'], min(time_horizon, schedule['end_year'] + 5)):
                    # 効果の蓄積（実装完了後も継続）
                    if year >= schedule['end_year']:
                        effect_factor = 1.0  # 完全効果
                    else:
                        # 実装期間中は段階的効果
                        progress = (year - schedule['start_year'] + 1) / (schedule['end_year'] - schedule['start_year'] + 1)
                        effect_factor = progress
                    
                    annual_effects[year, 0] += intensity * params['population_effect'] * effect_factor
                    annual_effects[year, 1] += intensity * params['economic_effect'] * effect_factor
                    annual_effects[year, 2] += intensity * params['livability_effect'] * effect_factor
            
            result = {
                'implementation_schedule': implementation_schedule,
                'annual_costs': total_annual_cost.tolist(),
                'annual_effects': {
                    'population': annual_effects[:, 0].tolist(),
                    'economic': annual_effects[:, 1].tolist(),
                    'livability': annual_effects[:, 2].tolist()
                },
                'total_scheduled_cost': sum(schedule['total_cost'] for schedule in implementation_schedule.values()),
                'unscheduled_policies': [
                    policy for policy in policy_allocation 
                    if policy_allocation[policy] > 0 and policy not in implementation_schedule
                ]
            }
            
            logger.info(f"政策タイミング最適化完了: {len(implementation_schedule)}政策スケジュール済み")
            return result
            
        except Exception as e:
            logger.error(f"政策タイミング最適化エラー: {e}")
            raise
    
    def sensitivity_analysis(self, 
                           optimal_allocation: Dict[str, float],
                           parameter_variations: Dict[str, float] = None) -> Dict:
        """
        感度分析
        
        Args:
            optimal_allocation: 最適配分
            parameter_variations: パラメータ変動幅（デフォルト±20%）
            
        Returns:
            感度分析結果
        """
        try:
            logger.info("感度分析開始")
            
            if parameter_variations is None:
                parameter_variations = {'cost': 0.2, 'effect': 0.2, 'budget': 0.1}
            
            base_effects = self._calculate_policy_effects(optimal_allocation)
            sensitivity_results = {}
            
            # コスト感度分析
            cost_sensitivity = {}
            for policy in optimal_allocation:
                if optimal_allocation[policy] > 0:
                    original_cost = self.policy_types[policy]['cost_per_unit']
                    
                    # コスト+20%
                    self.policy_types[policy]['cost_per_unit'] = original_cost * (1 + parameter_variations['cost'])
                    high_cost_result = self.optimize_budget_allocation()
                    
                    # コスト-20%
                    self.policy_types[policy]['cost_per_unit'] = original_cost * (1 - parameter_variations['cost'])
                    low_cost_result = self.optimize_budget_allocation()
                    
                    # 元に戻す
                    self.policy_types[policy]['cost_per_unit'] = original_cost
                    
                    cost_sensitivity[policy] = {
                        'high_cost_objective': high_cost_result['total_objective_value'],
                        'low_cost_objective': low_cost_result['total_objective_value'],
                        'sensitivity': (low_cost_result['total_objective_value'] - high_cost_result['total_objective_value']) / (2 * parameter_variations['cost'])
                    }
            
            sensitivity_results['cost_sensitivity'] = cost_sensitivity
            
            # 効果感度分析（簡略版）
            effect_sensitivity = {}
            for policy in optimal_allocation:
                if optimal_allocation[policy] > 0:
                    # 効果係数の変動による影響を計算
                    base_contribution = (
                        optimal_allocation[policy] * self.policy_types[policy]['population_effect'] +
                        optimal_allocation[policy] * self.policy_types[policy]['economic_effect'] +
                        optimal_allocation[policy] * self.policy_types[policy]['livability_effect']
                    )
                    
                    effect_sensitivity[policy] = {
                        'contribution_to_objective': base_contribution,
                        'relative_importance': base_contribution / sum(base_effects.values()) if sum(base_effects.values()) > 0 else 0
                    }
            
            sensitivity_results['effect_sensitivity'] = effect_sensitivity
            
            # 予算感度分析
            original_budget = self.constraints['total_budget']
            
            # 予算+10%
            self.constraints['total_budget'] = original_budget * (1 + parameter_variations['budget'])
            high_budget_result = self.optimize_budget_allocation()
            
            # 予算-10%
            self.constraints['total_budget'] = original_budget * (1 - parameter_variations['budget'])
            low_budget_result = self.optimize_budget_allocation()
            
            # 元に戻す
            self.constraints['total_budget'] = original_budget
            
            budget_sensitivity = {
                'high_budget_objective': high_budget_result['total_objective_value'],
                'low_budget_objective': low_budget_result['total_objective_value'],
                'budget_elasticity': (high_budget_result['total_objective_value'] - low_budget_result['total_objective_value']) / (2 * parameter_variations['budget'])
            }
            
            sensitivity_results['budget_sensitivity'] = budget_sensitivity
            
            logger.info("感度分析完了")
            return sensitivity_results
            
        except Exception as e:
            logger.error(f"感度分析エラー: {e}")
            raise
    
    def save_optimization_models(self, model_dir: str = "backend/data/models") -> None:
        """最適化モデル・設定の保存"""
        try:
            import os
            os.makedirs(model_dir, exist_ok=True)
            
            optimization_data = {
                'policy_types': self.policy_types,
                'constraints': self.constraints
            }
            
            file_path = f"{model_dir}/policy_optimizer_config.pkl"
            joblib.dump(optimization_data, file_path)
            
            logger.info("政策最適化設定保存完了")
            
        except Exception as e:
            logger.error(f"最適化モデル保存エラー: {e}")
            raise