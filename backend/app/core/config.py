from typing import List, Optional
from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "鳥取県住みやすさ創出プロジェクト"
    
    # セキュリティ
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-change-this")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8日間
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # メール設定
    MAIL_SERVER: Optional[str] = config("MAIL_SERVER", default=None)
    MAIL_PORT: int = config("MAIL_PORT", default=587, cast=int)
    MAIL_USERNAME: Optional[str] = config("MAIL_USERNAME", default=None)
    MAIL_PASSWORD: Optional[str] = config("MAIL_PASSWORD", default=None)
    MAIL_USE_TLS: bool = config("MAIL_USE_TLS", default=True, cast=bool)
    MAIL_FROM: str = config("MAIL_FROM", default="noreply@stat-tottori.jp")
    
    # セッション設定
    SESSION_TIMEOUT_HOURS: int = 24
    REMEMBER_ME_EXPIRE_DAYS: int = 30
    
    # CORS設定
    ALLOWED_HOSTS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # データベース設定
    DATABASE_URL: str = config(
        "DATABASE_URL", 
        default="postgresql://postgres:password@localhost:5432/stat_tottori"
    )
    
    # Redis設定
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379")
    
    # 外部API設定
    ESTAT_API_KEY: Optional[str] = config("ESTAT_API_KEY", default=None)
    RESAS_API_KEY: Optional[str] = config("RESAS_API_KEY", default=None)
    
    # ログ設定
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    
    # ファイルアップロード設定
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        case_sensitive = True


settings = Settings()