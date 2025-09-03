from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import logging

from app.models.user import User, UserSession, UserPreference, AnalysisHistory, ActivityLog, UserRole
from app.core.auth import auth_manager
import json

logger = logging.getLogger(__name__)

class UserService:
    """ユーザー関連サービスクラス"""
    
    def authenticate_user(
        self, 
        db: Session, 
        username_or_email: str, 
        password: str
    ) -> Optional[User]:
        """ユーザー認証"""
        try:
            # ユーザー名またはメールアドレスで検索
            user = db.query(User).filter(
                or_(User.username == username_or_email, User.email == username_or_email)
            ).first()
            
            if not user:
                return None
            
            # パスワード検証
            if not user.verify_password(password):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"ユーザー認証エラー: {e}")
            return None
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """ユーザーID でユーザー取得"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """ユーザー名でユーザー取得"""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """メールアドレスでユーザー取得"""
        return db.query(User).filter(User.email == email).first()
    
    def create_user(
        self, 
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        department: Optional[str] = None,
        organization: Optional[str] = None,
        role: UserRole = UserRole.VIEWER
    ) -> User:
        """新規ユーザー作成"""
        try:
            # 重複チェック
            existing_user = db.query(User).filter(
                or_(User.username == username, User.email == email)
            ).first()
            
            if existing_user:
                raise ValueError("ユーザー名またはメールアドレスが既に存在します")
            
            # ユーザー作成
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                department=department,
                organization=organization,
                role=role,
                email_verification_token=auth_manager.generate_verification_token()
            )
            user.set_password(password)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"新規ユーザー作成: {username}")
            return user
            
        except Exception as e:
            logger.error(f"ユーザー作成エラー: {e}")
            db.rollback()
            raise
    
    def update_user(
        self, 
        db: Session, 
        user: User, 
        update_data: Dict[str, Any]
    ) -> User:
        """ユーザー情報更新"""
        try:
            for key, value in update_data.items():
                if hasattr(user, key) and key not in ['id', 'created_at', 'hashed_password']:
                    setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"ユーザー情報更新: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"ユーザー更新エラー: {e}")
            db.rollback()
            raise
    
    def deactivate_user(self, db: Session, user: User) -> bool:
        """ユーザーを無効化"""
        try:
            user.is_active = False
            
            # 全セッションを無効化
            db.query(UserSession).filter(
                UserSession.user_id == user.id
            ).update({"is_active": False})
            
            db.commit()
            
            logger.info(f"ユーザー無効化: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザー無効化エラー: {e}")
            db.rollback()
            return False
    
    def get_user_preferences(self, db: Session, user_id: int) -> Dict[str, Any]:
        """ユーザー設定取得"""
        try:
            preferences = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).all()
            
            result = {}
            for pref in preferences:
                try:
                    # JSON形式の値をパース
                    result[pref.preference_key] = json.loads(pref.preference_value) if pref.preference_value else None
                except json.JSONDecodeError:
                    # JSON でない場合はそのまま文字列として保存
                    result[pref.preference_key] = pref.preference_value
            
            return result
            
        except Exception as e:
            logger.error(f"ユーザー設定取得エラー: {e}")
            return {}
    
    def update_user_preference(
        self, 
        db: Session, 
        user_id: int, 
        key: str, 
        value: Any
    ) -> bool:
        """ユーザー設定更新"""
        try:
            # 既存の設定を検索
            preference = db.query(UserPreference).filter(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.preference_key == key
                )
            ).first()
            
            # 値をJSON文字列に変換（必要に応じて）
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value) if value is not None else None
            
            if preference:
                # 既存設定を更新
                preference.preference_value = value_str
            else:
                # 新しい設定を作成
                preference = UserPreference(
                    user_id=user_id,
                    preference_key=key,
                    preference_value=value_str
                )
                db.add(preference)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"ユーザー設定更新エラー: {e}")
            db.rollback()
            return False
    
    def save_analysis_history(
        self, 
        db: Session,
        user_id: int,
        analysis_type: str,
        analysis_name: Optional[str] = None,
        parameters: Optional[Dict] = None,
        results: Optional[Dict] = None,
        execution_time: Optional[int] = None,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> AnalysisHistory:
        """分析履歴保存"""
        try:
            history = AnalysisHistory(
                user_id=user_id,
                analysis_type=analysis_type,
                analysis_name=analysis_name,
                parameters=json.dumps(parameters) if parameters else None,
                results=json.dumps(results) if results else None,
                execution_time=execution_time,
                status=status,
                error_message=error_message
            )
            
            db.add(history)
            db.commit()
            db.refresh(history)
            
            logger.info(f"分析履歴保存: ユーザー={user_id}, 種別={analysis_type}")
            return history
            
        except Exception as e:
            logger.error(f"分析履歴保存エラー: {e}")
            db.rollback()
            raise
    
    def get_user_analysis_history(
        self, 
        db: Session, 
        user_id: int, 
        limit: int = 50,
        analysis_type: Optional[str] = None
    ) -> List[AnalysisHistory]:
        """ユーザーの分析履歴取得"""
        try:
            query = db.query(AnalysisHistory).filter(
                AnalysisHistory.user_id == user_id
            )
            
            if analysis_type:
                query = query.filter(AnalysisHistory.analysis_type == analysis_type)
            
            histories = query.order_by(
                AnalysisHistory.created_at.desc()
            ).limit(limit).all()
            
            return histories
            
        except Exception as e:
            logger.error(f"分析履歴取得エラー: {e}")
            return []
    
    def toggle_analysis_favorite(
        self, 
        db: Session, 
        user_id: int, 
        analysis_id: int
    ) -> bool:
        """分析のお気に入り切り替え"""
        try:
            analysis = db.query(AnalysisHistory).filter(
                and_(
                    AnalysisHistory.id == analysis_id,
                    AnalysisHistory.user_id == user_id
                )
            ).first()
            
            if not analysis:
                return False
            
            analysis.is_favorite = not analysis.is_favorite
            db.commit()
            
            logger.info(f"お気に入り切り替え: 分析ID={analysis_id}, お気に入り={analysis.is_favorite}")
            return True
            
        except Exception as e:
            logger.error(f"お気に入り切り替えエラー: {e}")
            db.rollback()
            return False
    
    def get_user_favorites(self, db: Session, user_id: int) -> List[AnalysisHistory]:
        """ユーザーのお気に入り分析取得"""
        try:
            favorites = db.query(AnalysisHistory).filter(
                and_(
                    AnalysisHistory.user_id == user_id,
                    AnalysisHistory.is_favorite == True
                )
            ).order_by(AnalysisHistory.updated_at.desc()).all()
            
            return favorites
            
        except Exception as e:
            logger.error(f"お気に入り取得エラー: {e}")
            return []
    
    def log_user_activity(
        self, 
        db: Session,
        user_id: Optional[int],
        session_id: Optional[int],
        action: str,
        resource: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        status_code: Optional[int] = None,
        processing_time: Optional[int] = None
    ) -> ActivityLog:
        """ユーザーアクティビティログ記録"""
        try:
            log_entry = ActivityLog(
                user_id=user_id,
                session_id=session_id,
                action=action,
                resource=resource,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                status_code=status_code,
                processing_time=processing_time
            )
            
            db.add(log_entry)
            db.commit()
            
            return log_entry
            
        except Exception as e:
            logger.error(f"アクティビティログ記録エラー: {e}")
            db.rollback()
            raise
    
    def get_user_statistics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """ユーザー統計情報取得"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # 分析履歴統計
            total_analyses = db.query(AnalysisHistory).filter(
                AnalysisHistory.user_id == user_id
            ).count()
            
            favorite_analyses = db.query(AnalysisHistory).filter(
                and_(
                    AnalysisHistory.user_id == user_id,
                    AnalysisHistory.is_favorite == True
                )
            ).count()
            
            # 最近の活動
            recent_activities = db.query(ActivityLog).filter(
                ActivityLog.user_id == user_id
            ).filter(
                ActivityLog.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # 分析種別統計
            analysis_by_type = db.query(
                AnalysisHistory.analysis_type,
                func.count(AnalysisHistory.id).label('count')
            ).filter(
                AnalysisHistory.user_id == user_id
            ).group_by(AnalysisHistory.analysis_type).all()
            
            analysis_type_stats = {item.analysis_type: item.count for item in analysis_by_type}
            
            return {
                "user_info": {
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                    "login_count": user.login_count
                },
                "analysis_stats": {
                    "total_analyses": total_analyses,
                    "favorite_analyses": favorite_analyses,
                    "analysis_by_type": analysis_type_stats
                },
                "activity_stats": {
                    "recent_activities": recent_activities,
                    "account_age_days": (datetime.utcnow() - user.created_at).days if user.created_at else 0
                }
            }
            
        except Exception as e:
            logger.error(f"ユーザー統計取得エラー: {e}")
            return {}
    
    def search_users(
        self, 
        db: Session, 
        query: str, 
        role_filter: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        limit: int = 50
    ) -> List[User]:
        """ユーザー検索"""
        try:
            search_query = db.query(User)
            
            # テキスト検索
            if query:
                search_query = search_query.filter(
                    or_(
                        User.username.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%"),
                        User.full_name.ilike(f"%{query}%"),
                        User.organization.ilike(f"%{query}%")
                    )
                )
            
            # 権限フィルタ
            if role_filter:
                search_query = search_query.filter(User.role == role_filter)
            
            # アクティブ状態フィルタ
            if is_active is not None:
                search_query = search_query.filter(User.is_active == is_active)
            
            users = search_query.order_by(User.created_at.desc()).limit(limit).all()
            
            return users
            
        except Exception as e:
            logger.error(f"ユーザー検索エラー: {e}")
            return []