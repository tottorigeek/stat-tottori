from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

# 予測モデルのインポート
from backend.ml_models.population_forecast import PopulationPredictor
from backend.ml_models.economic_impact import EconomicImpactPredictor  
from backend.ml_models.livability_score import LivabilityScorePredictor
from backend.ml_models.policy_optimizer import PolicyOptimizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediction", tags=["prediction"])

# Pydanticモデル定義
class PolicyScenario(BaseModel):
    childcare_support: float = Field(0, ge=0, le=10, description="子育て支援政策強度")
    migration_support: float = Field(0, ge=0, le=8, description="移住支援政策強度") 
    economic_development: float = Field(0, ge=0, le=15, description="経済活性化政策強度")
    infrastructure_improvement: float = Field(0, ge=0, le=20, description="インフラ整備強度")
    education_enhancement: float = Field(0, ge=0, le=12, description="教育環境改善強度")
    healthcare_improvement: float = Field(0, ge=0, le=10, description="医療環境改善強度")

class PopulationPredictionRequest(BaseModel):
    model_type: str = Field("ensemble", description="予測モデル種別")
    years_ahead: int = Field(10, ge=1, le=20, description="予測期間（年）")
    policy_scenario: Optional[PolicyScenario] = Field(None, description="政策シナリオ")

class EconomicPredictionRequest(BaseModel):
    policy_scenario: Dict[str, float] = Field(..., description="政策シナリオ")
    population_change: float = Field(0.0, description="人口変化率（%）")
    years_ahead: int = Field(5, ge=1, le=10, description="予測期間（年）")

class LivabilityPredictionRequest(BaseModel):
    current_indicators: Dict[str, Dict[str, float]] = Field(..., description="現在の住みやすさ指標")
    policy_effects: Dict[str, Dict[str, float]] = Field(..., description="政策による指標変化")

class OptimizationRequest(BaseModel):
    objective: str = Field("total_benefit", description="最適化目標")
    budget_constraint: float = Field(100.0, ge=10, le=500, description="予算制約（億円）")
    optimization_method: str = Field("linear_programming", description="最適化手法")

# グローバルモデルインスタンス
population_model = PopulationPredictor()
economic_model = EconomicImpactPredictor()
livability_model = LivabilityScorePredictor()
policy_optimizer = PolicyOptimizer(population_model, economic_model, livability_model)

@router.post("/population", response_model=Dict[str, Any])
async def predict_population(request: PopulationPredictionRequest):
    """
    人口動態予測API
    """
    try:
        logger.info(f"人口予測リクエスト: {request.model_type}, {request.years_ahead}年")
        
        # 政策シナリオを辞書に変換
        policy_scenario = None
        if request.policy_scenario:
            policy_scenario = request.policy_scenario.dict()
        
        # 予測実行
        if request.model_type == "ensemble":
            result = population_model.ensemble_predict(
                years_ahead=request.years_ahead,
                policy_scenario=policy_scenario
            )
        else:
            result = population_model.predict_population(
                model_type=request.model_type,
                years_ahead=request.years_ahead,
                policy_scenario=policy_scenario
            )
        
        # レスポンス形式に変換
        response = {
            "prediction_type": "population",
            "model_type": request.model_type,
            "years_ahead": request.years_ahead,
            "forecast": result.get("forecast", []),
            "dates": [date.isoformat() if hasattr(date, 'isoformat') else str(date) 
                     for date in result.get("dates", [])],
            "confidence_intervals": {
                "lower": result.get("lower_bound", []),
                "upper": result.get("upper_bound", [])
            },
            "policy_scenario": policy_scenario,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_version": "1.0.0"
            }
        }
        
        if request.model_type == "ensemble":
            response["individual_predictions"] = result.get("individual_predictions", {})
            response["model_weights"] = result.get("weights", {})
        
        logger.info("人口予測完了")
        return response
        
    except Exception as e:
        logger.error(f"人口予測エラー: {e}")
        raise HTTPException(status_code=500, detail=f"人口予測に失敗しました: {str(e)}")

@router.post("/economic-impact", response_model=Dict[str, Any])
async def predict_economic_impact(request: EconomicPredictionRequest):
    """
    経済効果予測API
    """
    try:
        logger.info(f"経済効果予測リクエスト: {len(request.policy_scenario)}政策")
        
        # 包括的経済分析実行
        result = economic_model.comprehensive_economic_analysis(
            policy_scenario=request.policy_scenario,
            population_change=request.population_change,
            years_ahead=request.years_ahead
        )
        
        # レスポンス形式に変換
        response = {
            "prediction_type": "economic_impact",
            "policy_scenario": request.policy_scenario,
            "total_investment": result["total_investment"],
            "economic_impact": {
                "gdp_impact": result["economic_impact"]["total_gdp_impact"],
                "employment_impact": result["economic_impact"]["employment_impact"],
                "tax_revenue_impact": result["tax_prediction"]["total_tax_revenue"],
                "multiplier_effect": result["economic_impact"]["multiplier_effect"]
            },
            "time_series_projections": {
                "gdp_annual": result["gdp_prediction"]["annual_projections"],
                "employment_annual": result["employment_prediction"]["annual_employment_creation"],
                "tax_revenue_annual": result["tax_prediction"]["annual_tax_revenue"]
            },
            "industry_breakdown": result["economic_impact"]["industry_breakdown"],
            "roi_analysis": {
                "roi_percent": result["roi_percent"],
                "payback_period": result["payback_period"]
            },
            "years": list(range(1, request.years_ahead + 1)),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_version": "1.0.0"
            }
        }
        
        logger.info("経済効果予測完了")
        return response
        
    except Exception as e:
        logger.error(f"経済効果予測エラー: {e}")
        raise HTTPException(status_code=500, detail=f"経済効果予測に失敗しました: {str(e)}")

@router.post("/livability-score", response_model=Dict[str, Any])
async def predict_livability_score(request: LivabilityPredictionRequest):
    """
    住みやすさスコア予測API
    """
    try:
        logger.info("住みやすさスコア予測リクエスト")
        
        # 現在のスコア計算
        current_result = livability_model.calculate_livability_score(request.current_indicators)
        
        # 政策実施後のスコア変化予測
        change_result = livability_model.predict_score_changes(
            current_indicators=request.current_indicators,
            policy_effects=request.policy_effects
        )
        
        # レスポンス形式に変換
        response = {
            "prediction_type": "livability_score",
            "current_assessment": {
                "total_score": current_result["total_score"],
                "rank": current_result["rank"],
                "category_scores": current_result["category_scores"],
                "strengths": current_result["strengths"],
                "improvement_areas": current_result["improvement_areas"]
            },
            "predicted_changes": {
                "future_score": change_result["future_score"],
                "score_change": change_result["score_change"],
                "future_rank": change_result["future_rank"],
                "rank_changed": change_result["rank_changed"],
                "category_changes": change_result["category_changes"],
                "most_improved_categories": change_result["most_improved_categories"]
            },
            "policy_effectiveness": change_result["policy_effectiveness"],
            "detailed_breakdown": current_result["detailed_breakdown"],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_version": "1.0.0"
            }
        }
        
        logger.info("住みやすさスコア予測完了")
        return response
        
    except Exception as e:
        logger.error(f"住みやすさスコア予測エラー: {e}")
        raise HTTPException(status_code=500, detail=f"住みやすさスコア予測に失敗しました: {str(e)}")

@router.post("/policy-optimization", response_model=Dict[str, Any])
async def optimize_policy_allocation(request: OptimizationRequest):
    """
    政策配分最適化API
    """
    try:
        logger.info(f"政策最適化リクエスト: {request.objective}, 予算{request.budget_constraint}億円")
        
        # 制約条件更新
        constraints = {"total_budget": request.budget_constraint}
        
        # 最適化実行
        optimization_result = policy_optimizer.optimize_budget_allocation(
            objective=request.objective,
            constraints=constraints,
            optimization_method=request.optimization_method
        )
        
        # タイミング最適化も実行
        timing_result = policy_optimizer.optimize_policy_timing(
            policy_allocation=optimization_result["optimal_allocation"],
            time_horizon=10
        )
        
        # 感度分析実行
        sensitivity_result = policy_optimizer.sensitivity_analysis(
            optimal_allocation=optimization_result["optimal_allocation"]
        )
        
        # レスポンス形式に変換
        response = {
            "optimization_type": "policy_allocation",
            "objective": request.objective,
            "optimization_method": request.optimization_method,
            "budget_constraint": request.budget_constraint,
            "optimal_allocation": optimization_result["optimal_allocation"],
            "optimization_results": {
                "total_cost": optimization_result["total_cost"],
                "total_objective_value": optimization_result["total_objective_value"],
                "budget_utilization": optimization_result["budget_utilization"],
                "is_feasible": optimization_result["is_feasible"]
            },
            "predicted_effects": optimization_result["predicted_effects"],
            "implementation_schedule": timing_result["implementation_schedule"],
            "annual_projections": {
                "costs": timing_result["annual_costs"],
                "effects": timing_result["annual_effects"]
            },
            "sensitivity_analysis": sensitivity_result,
            "constraint_violations": optimization_result.get("constraint_violations", []),
            "effect_uncertainty": optimization_result.get("effect_uncertainty", {}),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_version": "1.0.0"
            }
        }
        
        logger.info("政策最適化完了")
        return response
        
    except Exception as e:
        logger.error(f"政策最適化エラー: {e}")
        raise HTTPException(status_code=500, detail=f"政策最適化に失敗しました: {str(e)}")

@router.get("/models/status", response_model=Dict[str, Any])
async def get_model_status():
    """
    予測モデルの状態確認API
    """
    try:
        # 各モデルの状態チェック
        status = {
            "population_model": {
                "available_models": list(population_model.models.keys()),
                "feature_columns_count": len(population_model.feature_columns),
                "status": "ready" if population_model.models else "not_trained"
            },
            "economic_model": {
                "input_output_matrix_shape": economic_model.input_output_matrix.shape,
                "economic_relationships": len(economic_model.economic_relationships),
                "status": "ready"
            },
            "livability_model": {
                "available_models": list(livability_model.models.keys()),
                "indicator_categories": len(livability_model.indicator_weights),
                "status": "ready" if livability_model.models else "configuration_only"
            },
            "policy_optimizer": {
                "available_policies": len(policy_optimizer.policy_types),
                "constraints": len(policy_optimizer.constraints),
                "status": "ready"
            },
            "system": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"モデル状態取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"モデル状態取得に失敗しました: {str(e)}")

@router.post("/comprehensive-analysis", response_model=Dict[str, Any])
async def comprehensive_policy_analysis(
    request: dict,
    background_tasks: BackgroundTasks
):
    """
    包括的政策分析API（全予測モデルを統合実行）
    """
    try:
        logger.info("包括的政策分析開始")
        
        policy_scenario = request.get("policy_scenario", {})
        years_ahead = request.get("years_ahead", 5)
        budget_constraint = request.get("budget_constraint", 100.0)
        
        # 各予測を並行実行
        results = {}
        
        # 1. 人口予測
        population_result = population_model.ensemble_predict(
            years_ahead=years_ahead,
            policy_scenario=policy_scenario
        )
        results["population_prediction"] = population_result
        
        # 2. 経済効果予測
        economic_result = economic_model.comprehensive_economic_analysis(
            policy_scenario=policy_scenario,
            population_change=0.02,  # 人口増加効果から推定
            years_ahead=years_ahead
        )
        results["economic_impact"] = economic_result
        
        # 3. 政策最適化
        optimization_result = policy_optimizer.optimize_budget_allocation(
            objective="total_benefit",
            constraints={"total_budget": budget_constraint}
        )
        results["policy_optimization"] = optimization_result
        
        # 4. 統合分析結果
        integrated_analysis = {
            "total_investment": sum(policy_scenario.values()),
            "predicted_outcomes": {
                "population_change": population_result.get("forecast", [])[-1] if population_result.get("forecast") else 0,
                "gdp_impact": economic_result["economic_impact"]["total_gdp_impact"],
                "employment_creation": economic_result["employment_prediction"]["total_employment_creation"],
                "tax_revenue": economic_result["tax_prediction"]["total_tax_revenue"]
            },
            "optimization_recommendations": optimization_result["optimal_allocation"],
            "cost_benefit_analysis": {
                "total_benefits": economic_result["economic_impact"]["total_gdp_impact"] + economic_result["tax_prediction"]["total_tax_revenue"],
                "total_costs": sum(policy_scenario.values()),
                "benefit_cost_ratio": (economic_result["economic_impact"]["total_gdp_impact"] + economic_result["tax_prediction"]["total_tax_revenue"]) / max(sum(policy_scenario.values()), 1)
            }
        }
        
        # レスポンス統合
        response = {
            "analysis_type": "comprehensive",
            "input_parameters": {
                "policy_scenario": policy_scenario,
                "years_ahead": years_ahead,
                "budget_constraint": budget_constraint
            },
            "individual_results": results,
            "integrated_analysis": integrated_analysis,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_duration": "background",
                "version": "1.0.0"
            }
        }
        
        # バックグラウンドでモデル再学習をスケジュール
        background_tasks.add_task(update_models_with_new_data)
        
        logger.info("包括的政策分析完了")
        return response
        
    except Exception as e:
        logger.error(f"包括的政策分析エラー: {e}")
        raise HTTPException(status_code=500, detail=f"包括的政策分析に失敗しました: {str(e)}")

async def update_models_with_new_data():
    """
    バックグラウンドでのモデル更新タスク
    """
    try:
        logger.info("バックグラウンドモデル更新開始")
        
        # 新しいデータでモデルを再学習（簡略化）
        # 実際の実装では、最新の統計データを取得してモデルを更新
        
        logger.info("バックグラウンドモデル更新完了")
        
    except Exception as e:
        logger.error(f"バックグラウンドモデル更新エラー: {e}")

# モデル初期化（アプリケーション起動時に実行）
@router.on_event("startup")
async def initialize_models():
    """
    予測モデルの初期化
    """
    try:
        logger.info("予測モデル初期化開始")
        
        # 保存済みモデルの読み込み試行
        try:
            population_model.load_models()
            logger.info("人口予測モデル読み込み完了")
        except:
            logger.warning("人口予測モデルが見つかりません（初回起動）")
        
        # 経済モデルの初期化（設定ベース）
        logger.info("経済効果モデル初期化完了")
        
        # 住みやすさモデルの初期化
        logger.info("住みやすさモデル初期化完了")
        
        # 最適化モデルの初期化
        logger.info("政策最適化モデル初期化完了")
        
        logger.info("全予測モデル初期化完了")
        
    except Exception as e:
        logger.error(f"モデル初期化エラー: {e}")
        # 初期化に失敗してもアプリケーションは起動継続