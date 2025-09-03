from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

# 認証関連スキーマ
class UserRegister(BaseModel):
    """ユーザー登録リクエストスキーマ"""
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, max_length=128, description="パスワード")
    full_name: Optional[str] = Field(None, max_length=100, description="氏名")
    department: Optional[str] = Field(None, max_length=100, description="所属部署")
    organization: Optional[str] = Field(None, max_length=100, description="所属組織")

    @validator('password')
    def validate_password(cls, v):
        """パスワード強度チェック"""
        if len(v) < 8:
            raise ValueError('パスワードは8文字以上である必要があります')
        if not any(c.isupper() for c in v):
            raise ValueError('パスワードには大文字を含める必要があります')
        if not any(c.islower() for c in v):
            raise ValueError('パスワードには小文字を含める必要があります')
        if not any(c.isdigit() for c in v):
            raise ValueError('パスワードには数字を含める必要があります')
        return v

    @validator('username')
    def validate_username(cls, v):
        """ユーザー名形式チェック"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('ユーザー名は英数字、アンダースコア、ハイフンのみ使用可能です')
        return v.lower()

class UserLogin(BaseModel):
    """ログインリクエストスキーマ"""
    username_or_email: str = Field(..., description="ユーザー名またはメールアドレス")
    password: str = Field(..., description="パスワード")
    remember_me: bool = Field(False, description="ログイン状態を保持")

class PasswordReset(BaseModel):
    """パスワードリセットリクエストスキーマ"""
    email: EmailStr = Field(..., description="メールアドレス")

class PasswordResetConfirm(BaseModel):
    """パスワードリセット確認スキーマ"""
    token: str = Field(..., description="リセットトークン")
    new_password: str = Field(..., min_length=8, max_length=128, description="新しいパスワード")

    @validator('new_password')
    def validate_password(cls, v):
        """パスワード強度チェック"""
        if len(v) < 8:
            raise ValueError('パスワードは8文字以上である必要があります')
        if not any(c.isupper() for c in v):
            raise ValueError('パスワードには大文字を含める必要があります')
        if not any(c.islower() for c in v):
            raise ValueError('パスワードには小文字を含める必要があります')
        if not any(c.isdigit() for c in v):
            raise ValueError('パスワードには数字を含める必要があります')
        return v

class EmailVerification(BaseModel):
    """メール認証リクエストスキーマ"""
    token: str = Field(..., description="認証トークン")

# レスポンススキーマ
class Token(BaseModel):
    """トークンレスポンススキーマ"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒数
    refresh_token: Optional[str] = None

class UserResponse(BaseModel):
    """ユーザー情報レスポンススキーマ"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    department: Optional[str]
    organization: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    language: str
    timezone: str
    notification_email: bool
    theme: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    last_activity: Optional[datetime]
    login_count: int

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """ユーザープロフィール更新スキーマ"""
    full_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, regex="^(ja|en)$")
    timezone: Optional[str] = Field(None, max_length=50)
    notification_email: Optional[bool] = None
    theme: Optional[str] = Field(None, regex="^(light|dark|auto)$")

class PasswordChange(BaseModel):
    """パスワード変更スキーマ"""
    current_password: str = Field(..., description="現在のパスワード")
    new_password: str = Field(..., min_length=8, max_length=128, description="新しいパスワード")

    @validator('new_password')
    def validate_password(cls, v):
        """パスワード強度チェック"""
        if len(v) < 8:
            raise ValueError('パスワードは8文字以上である必要があります')
        if not any(c.isupper() for c in v):
            raise ValueError('パスワードには大文字を含める必要があります')
        if not any(c.islower() for c in v):
            raise ValueError('パスワードには小文字を含める必要があります')
        if not any(c.isdigit() for c in v):
            raise ValueError('パスワードには数字を含める必要があります')
        return v

# セッション管理スキーマ
class SessionResponse(BaseModel):
    """セッション情報レスポンススキーマ"""
    id: int
    device_info: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_active: bool
    expires_at: datetime
    created_at: datetime
    last_accessed: Optional[datetime]
    is_current: bool = False

class UserPreferenceItem(BaseModel):
    """ユーザー設定項目スキーマ"""
    key: str = Field(..., max_length=100)
    value: Optional[str] = None

class UserPreferenceBatch(BaseModel):
    """ユーザー設定一括更新スキーマ"""
    preferences: List[UserPreferenceItem]

# 分析履歴スキーマ
class AnalysisHistoryResponse(BaseModel):
    """分析履歴レスポンススキーマ"""
    id: int
    analysis_type: str
    analysis_name: Optional[str]
    parameters: Optional[str]  # JSON文字列
    results: Optional[str]     # JSON文字列
    execution_time: Optional[int]
    status: str
    error_message: Optional[str]
    is_favorite: bool
    is_shared: bool
    share_token: Optional[str]
    created_at: datetime
    updated_at: datetime

class AnalysisHistoryCreate(BaseModel):
    """分析履歴作成スキーマ"""
    analysis_type: str = Field(..., max_length=50)
    analysis_name: Optional[str] = Field(None, max_length=200)
    parameters: Optional[dict] = None
    results: Optional[dict] = None
    execution_time: Optional[int] = None
    status: str = Field("completed", max_length=20)
    error_message: Optional[str] = None

class AnalysisHistoryUpdate(BaseModel):
    """分析履歴更新スキーマ"""
    analysis_name: Optional[str] = Field(None, max_length=200)
    is_favorite: Optional[bool] = None
    is_shared: Optional[bool] = None

# アクティビティログスキーマ
class ActivityLogResponse(BaseModel):
    """アクティビティログレスポンススキーマ"""
    id: int
    action: str
    resource: Optional[str]
    details: Optional[str]  # JSON文字列
    ip_address: Optional[str]
    user_agent: Optional[str]
    referer: Optional[str]
    status_code: Optional[int]
    processing_time: Optional[int]
    created_at: datetime

# 管理者向けスキーマ
class UserManagement(BaseModel):
    """ユーザー管理（管理者用）スキーマ"""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserListResponse(BaseModel):
    """ユーザー一覧レスポンススキーマ"""
    users: List[UserResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int

class UserStats(BaseModel):
    """ユーザー統計スキーマ"""
    total_users: int
    active_users: int
    verified_users: int
    users_by_role: dict
    recent_registrations: int
    recent_logins: int