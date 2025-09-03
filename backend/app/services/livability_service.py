from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from app.models.livability import LivabilityScore, LivabilityIndicator, UserLivabilityWeight
from app.schemas.livability import LivabilityScoreResponse, LivabilityIndicatorResponse
import json


class LivabilityService:
    """住みやすさ関連サービス"""

    async def get_livability_scores(
        self,
        db: Session,
        prefecture_code: str,
        municipality_code: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[LivabilityScoreResponse]:
        """住みやすさスコアを取得する"""
        
        query = db.query(LivabilityScore).filter(
            LivabilityScore.prefecture_code == prefecture_code
        )
        
        if municipality_code:
            query = query.filter(LivabilityScore.municipality_code == municipality_code)
        
        if year:
            query = query.filter(LivabilityScore.year == year)
        else:
            # 最新年のデータを取得
            latest_year = db.query(func.max(LivabilityScore.year)).filter(
                LivabilityScore.prefecture_code == prefecture_code
            ).scalar()
            if latest_year:
                query = query.filter(LivabilityScore.year == latest_year)
        
        query = query.order_by(desc(LivabilityScore.total_score))
        scores = query.all()
        
        return [LivabilityScoreResponse.from_orm(score) for score in scores]

    async def get_livability_comparison(
        self,
        db: Session,
        municipality_codes: List[str],
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """複数地域の住みやすさ比較データを取得する"""
        
        query = db.query(LivabilityScore).filter(
            LivabilityScore.municipality_code.in_(municipality_codes)
        )
        
        if year:
            query = query.filter(LivabilityScore.year == year)
        else:
            # 最新年のデータを取得
            latest_year = db.query(func.max(LivabilityScore.year)).scalar()
            if latest_year:
                query = query.filter(LivabilityScore.year == latest_year)
        
        scores = query.all()
        
        result = []
        sorted_scores = sorted(scores, key=lambda x: x.total_score, reverse=True)
        
        for idx, score in enumerate(sorted_scores):
            result.append({
                "municipality_code": score.municipality_code,
                "municipality_name": self._get_municipality_name(score.municipality_code),
                "total_score": score.total_score,
                "category_scores": {
                    "infrastructure": score.infrastructure_score,
                    "healthcare": score.healthcare_score,
                    "education": score.education_score,
                    "environment": score.environment_score,
                    "economy": score.economy_score,
                    "community": score.community_score,
                    "transport": score.transport_score,
                    "culture": score.culture_score
                },
                "rank": idx + 1,
                "percentile": (len(sorted_scores) - idx) / len(sorted_scores) * 100
            })
        
        return result

    async def get_radar_chart_data(
        self,
        db: Session,
        municipality_code: str,
        year: Optional[int] = None,
        user_weights: Optional[str] = None
    ) -> Dict[str, Any]:
        """レーダーチャート用データを取得する"""
        
        query = db.query(LivabilityScore).filter(
            LivabilityScore.municipality_code == municipality_code
        )
        
        if year:
            query = query.filter(LivabilityScore.year == year)
        else:
            # 最新年のデータを取得
            latest_year = db.query(func.max(LivabilityScore.year)).filter(
                LivabilityScore.municipality_code == municipality_code
            ).scalar()
            if latest_year:
                query = query.filter(LivabilityScore.year == latest_year)
        
        score_data = query.first()
        
        if not score_data:
            raise ValueError("指定された地域・年のデータが見つかりません")
        
        # カテゴリー別スコア（0-100スケール）
        scores = [
            score_data.infrastructure_score or 0,
            score_data.healthcare_score or 0,
            score_data.education_score or 0,
            score_data.environment_score or 0,
            score_data.economy_score or 0,
            score_data.community_score or 0,
            score_data.transport_score or 0,
            score_data.culture_score or 0
        ]
        
        # ユーザー重みが指定されている場合は重み付けスコアを計算
        if user_weights:
            try:
                weights = json.loads(user_weights)
                weighted_scores = []
                weight_keys = [
                    "infrastructure_weight", "healthcare_weight", "education_weight",
                    "environment_weight", "economy_weight", "community_weight",
                    "transport_weight", "culture_weight"
                ]
                
                for i, score in enumerate(scores):
                    weight = weights.get(weight_keys[i], 1.0)
                    weighted_scores.append(score * weight)
                
                scores = weighted_scores
            except (json.JSONDecodeError, KeyError):
                # JSON解析エラーの場合は元のスコアを使用
                pass
        
        return {
            "municipality_name": self._get_municipality_name(municipality_code),
            "scores": scores
        }

    async def get_indicators(
        self,
        db: Session,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[LivabilityIndicatorResponse]:
        """住みやすさ指標マスターデータを取得する"""
        
        query = db.query(LivabilityIndicator)
        
        if category:
            query = query.filter(LivabilityIndicator.category == category)
        
        if active_only:
            query = query.filter(LivabilityIndicator.is_active == True)
        
        query = query.order_by(LivabilityIndicator.category, LivabilityIndicator.indicator_name)
        indicators = query.all()
        
        return [LivabilityIndicatorResponse.from_orm(indicator) for indicator in indicators]

    async def calculate_custom_score(
        self,
        db: Session,
        municipality_code: str,
        custom_weights: Dict[str, float],
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """カスタム重みで住みやすさスコアを計算する"""
        
        # 基本スコアデータを取得
        query = db.query(LivabilityScore).filter(
            LivabilityScore.municipality_code == municipality_code
        )
        
        if year:
            query = query.filter(LivabilityScore.year == year)
        else:
            latest_year = db.query(func.max(LivabilityScore.year)).filter(
                LivabilityScore.municipality_code == municipality_code
            ).scalar()
            if latest_year:
                query = query.filter(LivabilityScore.year == latest_year)
        
        base_score = query.first()
        
        if not base_score:
            raise ValueError("基準となるスコアデータが見つかりません")
        
        # カスタム重みを適用してスコアを計算
        category_scores = {
            "infrastructure": base_score.infrastructure_score or 0,
            "healthcare": base_score.healthcare_score or 0,
            "education": base_score.education_score or 0,
            "environment": base_score.environment_score or 0,
            "economy": base_score.economy_score or 0,
            "community": base_score.community_score or 0,
            "transport": base_score.transport_score or 0,
            "culture": base_score.culture_score or 0
        }
        
        weighted_scores = {}
        total_weight = 0
        weighted_total = 0
        
        for category, score in category_scores.items():
            weight = custom_weights.get(f"{category}_weight", 1.0)
            weighted_score = score * weight
            weighted_scores[category] = weighted_score
            total_weight += weight
            weighted_total += weighted_score
        
        # 正規化された総合スコア
        normalized_total_score = weighted_total / total_weight if total_weight > 0 else 0
        
        return {
            "municipality_code": municipality_code,
            "municipality_name": self._get_municipality_name(municipality_code),
            "custom_total_score": normalized_total_score,
            "category_weighted_scores": weighted_scores,
            "applied_weights": custom_weights,
            "original_total_score": base_score.total_score
        }

    def _get_municipality_name(self, municipality_code: str) -> str:
        """市町村コードから名称を取得する（仮実装）"""
        # 実際の実装では、市町村マスターテーブルから名称を取得
        municipality_names = {
            "31201": "鳥取市",
            "31202": "米子市",
            "31203": "倉吉市",
            "31204": "境港市",
            # その他の市町村コードを追加
        }
        return municipality_names.get(municipality_code, f"市町村({municipality_code})")