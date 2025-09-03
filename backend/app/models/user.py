from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from passlib.context import CryptContext
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    """ユーザー権限enum"""
    ADMIN = "admin"           # 管理者（全権限）
    ANALYST = "analyst"       # 分析者（分析・レポート作成権限）
    VIEWER = "viewer"         # 閲覧者（閲覧のみ）
    POLICY_MAKER = "policy_maker"  # 政策立案者（予測・最適化権限）

class User(Base):
    """ユーザーモデル"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)  # 所属部署
    organization = Column(String(100), nullable=True)  # 所属組織
    
    # 権限・ステータス
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # 認証関連
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # 個人設定
    language = Column(String(10), default="ja", nullable=False)  # 言語設定
    timezone = Column(String(50), default="Asia/Tokyo", nullable=False)  # タイムゾーン
    notification_email = Column(Boolean, default=True, nullable=False)  # メール通知設定
    theme = Column(String(20), default="light", nullable=False)  # テーマ設定
    
    # メタデータ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity = Column(DateTime, nullable=True)
    
    # パスワードハッシュ化用
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def set_password(self, password: str) -> None:
        """パスワードをハッシュ化して設定"""
        self.hashed_password = self.pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """パスワードの検証"""
        return self.pwd_context.verify(password, self.hashed_password)
    
    def update_last_login(self) -> None:
        """最終ログイン時刻とカウントを更新"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.last_activity = datetime.utcnow()
    
    def has_permission(self, required_role: UserRole) -> bool:
        """権限チェック"""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.ANALYST: 2,
            UserRole.POLICY_MAKER: 3,
            UserRole.ADMIN: 4
        }
        
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def to_dict(self) -> dict:
        """ユーザー情報を辞書形式で返す（パスワードは除外）"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "department": self.department,
            "organization": self.organization,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "language": self.language,
            "timezone": self.timezone,
            "notification_email": self.notification_email,
            "theme": self.theme,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "login_count": self.login_count
        }

class UserSession(Base):
    """ユーザーセッションモデル"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    device_info = Column(Text, nullable=True)  # ブラウザ・デバイス情報
    ip_address = Column(String(45), nullable=True)  # IPv6対応
    user_agent = Column(Text, nullable=True)
    
    # セッション管理
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    
    def is_expired(self) -> bool:
        """セッションが期限切れかどうか"""
        return datetime.utcnow() > self.expires_at
    
    def update_last_accessed(self) -> None:
        """最終アクセス時刻を更新"""
        self.last_accessed = datetime.utcnow()

class UserPreference(Base):
    """ユーザー個人設定モデル"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class AnalysisHistory(Base):
    """分析履歴モデル"""
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)  # 分析種別
    analysis_name = Column(String(200), nullable=True)  # 分析名
    parameters = Column(Text, nullable=True)  # 分析パラメータ（JSON）
    results = Column(Text, nullable=True)  # 分析結果（JSON）
    
    # メタデータ
    execution_time = Column(Integer, nullable=True)  # 実行時間（ミリ秒）
    status = Column(String(20), default="completed", nullable=False)  # completed, failed, running
    error_message = Column(Text, nullable=True)
    
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_shared = Column(Boolean, default=False, nullable=False)
    share_token = Column(String(255), unique=True, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ActivityLog(Base):
    """ユーザーアクティビティログモデル"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # 匿名アクセスの場合はNull
    session_id = Column(Integer, nullable=True, index=True)
    
    # アクティビティ情報
    action = Column(String(50), nullable=False)  # login, logout, view_page, run_analysis等
    resource = Column(String(100), nullable=True)  # アクセスしたリソース
    details = Column(Text, nullable=True)  # 詳細情報（JSON）
    
    # リクエスト情報
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)
    
    # ステータス
    status_code = Column(Integer, nullable=True)  # HTTPステータスコード
    processing_time = Column(Integer, nullable=True)  # 処理時間（ミリ秒）
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)