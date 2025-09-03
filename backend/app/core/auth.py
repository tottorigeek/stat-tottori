from datetime import datetime, timedelta
from typing import Optional, Union
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets
import string
from app.core.config import settings
from app.models.user import User, UserSession, UserRole
from app.db.database import get_db
import logging

logger = logging.getLogger(__name__)

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer認証
security = HTTPBearer()

class AuthManager:
    """認証管理クラス"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """アクセストークン生成"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"アクセストークン生成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="トークン生成に失敗しました"
            )
    
    def create_refresh_token(self, data: dict) -> str:
        """リフレッシュトークン生成"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"リフレッシュトークン生成エラー: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="リフレッシュトークン生成に失敗しました"
            )
    
    def verify_token(self, token: str, expected_type: str = "access") -> Optional[dict]:
        """トークン検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # トークンタイプチェック
            token_type = payload.get("type")
            if token_type != expected_type:
                return None
            
            # 有効期限チェック
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
        
        except InvalidTokenError:
            return None
        except Exception as e:
            logger.error(f"トークン検証エラー: {e}")
            return None
    
    def generate_verification_token(self) -> str:
        """メール認証用トークン生成"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def generate_reset_token(self) -> str:
        """パスワードリセット用トークン生成"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def hash_password(self, password: str) -> str:
        """パスワードハッシュ化"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        return pwd_context.verify(plain_password, hashed_password)

# AuthManagerのインスタンス
auth_manager = AuthManager()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """現在のユーザーを取得"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証に失敗しました",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # トークンからペイロード取得
        payload = auth_manager.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # データベースからユーザー取得
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
        
        # ユーザーがアクティブかチェック
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="アカウントが無効です"
            )
        
        # 最終活動時刻を更新
        user.last_activity = datetime.utcnow()
        db.commit()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ユーザー取得エラー: {e}")
        raise credentials_exception

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """現在のアクティブユーザーを取得"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="アカウントが無効です"
        )
    return current_user

def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """現在の認証済みユーザーを取得"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メール認証が必要です"
        )
    return current_user

class RequireRole:
    """権限チェック用デコレータクラス"""
    
    def __init__(self, required_role: UserRole):
        self.required_role = required_role
    
    def __call__(self, current_user: User = Depends(get_current_verified_user)):
        if not current_user.has_permission(self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"この機能には{self.required_role.value}権限が必要です"
            )
        return current_user

# 権限チェック関数
def require_admin(current_user: User = Depends(get_current_verified_user)) -> User:
    """管理者権限が必要"""
    return RequireRole(UserRole.ADMIN)(current_user)

def require_analyst(current_user: User = Depends(get_current_verified_user)) -> User:
    """分析者権限が必要"""
    return RequireRole(UserRole.ANALYST)(current_user)

def require_policy_maker(current_user: User = Depends(get_current_verified_user)) -> User:
    """政策立案者権限が必要"""
    return RequireRole(UserRole.POLICY_MAKER)(current_user)

class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self):
        self.session_expire_hours = 24  # デフォルト24時間
        self.remember_me_expire_days = 30  # Remember me: 30日
    
    def create_session(
        self, 
        db: Session, 
        user_id: int, 
        request: Request,
        remember_me: bool = False
    ) -> UserSession:
        """新しいセッションを作成"""
        
        # セッショントークン生成
        session_token = secrets.token_urlsafe(32)
        
        # 有効期限設定
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=self.remember_me_expire_days)
        else:
            expires_at = datetime.utcnow() + timedelta(hours=self.session_expire_hours)
        
        # セッション情報作成
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            device_info=self._get_device_info(request),
            expires_at=expires_at,
            last_accessed=datetime.utcnow()
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def validate_session(self, db: Session, session_token: str) -> Optional[UserSession]:
        """セッション検証"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if not session or session.is_expired():
            return None
        
        # 最終アクセス時刻更新
        session.update_last_accessed()
        db.commit()
        
        return session
    
    def invalidate_session(self, db: Session, session_token: str) -> bool:
        """セッション無効化"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    def invalidate_user_sessions(self, db: Session, user_id: int, except_token: str = None) -> int:
        """ユーザーの全セッションを無効化（指定トークン以外）"""
        query = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        )
        
        if except_token:
            query = query.filter(UserSession.session_token != except_token)
        
        sessions = query.all()
        count = 0
        
        for session in sessions:
            session.is_active = False
            count += 1
        
        db.commit()
        return count
    
    def cleanup_expired_sessions(self, db: Session) -> int:
        """期限切れセッションのクリーンアップ"""
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_active == True
        ).all()
        
        count = 0
        for session in expired_sessions:
            session.is_active = False
            count += 1
        
        db.commit()
        return count
    
    def _get_client_ip(self, request: Request) -> str:
        """クライアントIPアドレス取得"""
        # プロキシ経由の場合を考慮
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_device_info(self, request: Request) -> str:
        """デバイス情報取得（簡易版）"""
        user_agent = request.headers.get("User-Agent", "")
        
        # 簡易的なデバイス判定
        if "Mobile" in user_agent or "Android" in user_agent:
            return "Mobile"
        elif "Tablet" in user_agent or "iPad" in user_agent:
            return "Tablet"
        else:
            return "Desktop"

# SessionManagerのインスタンス
session_manager = SessionManager()