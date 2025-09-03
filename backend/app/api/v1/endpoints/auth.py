from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
import logging

from app.db.database import get_db
from app.models.user import User, UserSession, UserRole, ActivityLog
from app.schemas.auth import (
    UserRegister, UserLogin, PasswordReset, PasswordResetConfirm, 
    EmailVerification, Token, UserResponse, UserProfile, PasswordChange,
    SessionResponse, AnalysisHistoryResponse, ActivityLogResponse
)
from app.core.auth import (
    auth_manager, get_current_user, get_current_active_user, 
    get_current_verified_user, session_manager, require_admin
)
from app.services.email_service import send_verification_email, send_password_reset_email
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# ユーザーサービスインスタンス
user_service = UserService()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """新規ユーザー登録"""
    try:
        # ユーザー名・メールアドレス重複チェック
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ユーザー名は既に使用されています"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="メールアドレスは既に使用されています"
                )
        
        # 新規ユーザー作成
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            department=user_data.department,
            organization=user_data.organization,
            role=UserRole.VIEWER,  # デフォルト権限
            email_verification_token=auth_manager.generate_verification_token()
        )
        new_user.set_password(user_data.password)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # メール認証送信（バックグラウンド）
        background_tasks.add_task(
            send_verification_email,
            new_user.email,
            new_user.email_verification_token,
            new_user.full_name or new_user.username
        )
        
        logger.info(f"新規ユーザー登録: {new_user.username} ({new_user.email})")
        
        return {
            "message": "ユーザー登録が完了しました。メール認証を行ってください。",
            "user_id": new_user.id,
            "email": new_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ユーザー登録エラー: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー登録に失敗しました"
        )

@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """ユーザーログイン"""
    try:
        # ユーザー認証
        user = user_service.authenticate_user(
            db, login_data.username_or_email, login_data.password
        )
        
        if not user:
            # アクティビティログ記録（失敗）
            log_entry = ActivityLog(
                action="login_failed",
                details=f"{{\"username_or_email\": \"{login_data.username_or_email}\"}}",
                ip_address=session_manager._get_client_ip(request),
                user_agent=request.headers.get("User-Agent"),
                status_code=401
            )
            db.add(log_entry)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザー名またはパスワードが正しくません"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="アカウントが無効化されています"
            )
        
        # アクセストークン生成
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        # リフレッシュトークン生成
        refresh_token = auth_manager.create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        # セッション作成
        session = session_manager.create_session(
            db, user.id, request, login_data.remember_me
        )
        
        # ユーザー最終ログイン更新
        user.update_last_login()
        db.commit()
        
        # アクティビティログ記録（成功）
        log_entry = ActivityLog(
            user_id=user.id,
            session_id=session.id,
            action="login_success",
            details=f"{{\"remember_me\": {login_data.remember_me}}}",
            ip_address=session_manager._get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            status_code=200
        )
        db.add(log_entry)
        db.commit()
        
        logger.info(f"ユーザーログイン: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_token_expires.total_seconds(),
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ログインエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログインに失敗しました"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザーログアウト"""
    try:
        # セッショントークン取得
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            
            # セッション無効化
            session_manager.invalidate_session(db, token)
        
        # アクティビティログ記録
        log_entry = ActivityLog(
            user_id=current_user.id,
            action="logout",
            ip_address=session_manager._get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            status_code=200
        )
        db.add(log_entry)
        db.commit()
        
        logger.info(f"ユーザーログアウト: {current_user.username}")
        
        return {"message": "ログアウトしました"}
        
    except Exception as e:
        logger.error(f"ログアウトエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログアウトに失敗しました"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """アクセストークン更新"""
    try:
        # リフレッシュトークン検証
        payload = auth_manager.verify_token(refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なリフレッシュトークンです"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つからないか無効です"
            )
        
        # 新しいアクセストークン生成
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"トークン更新エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークン更新に失敗しました"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """現在のユーザー情報取得"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """プロフィール更新"""
    try:
        # プロフィール情報更新
        update_data = profile_data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"プロフィール更新: {current_user.username}")
        
        return current_user
        
    except Exception as e:
        logger.error(f"プロフィール更新エラー: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="プロフィール更新に失敗しました"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """パスワード変更"""
    try:
        # 現在のパスワード確認
        if not current_user.verify_password(password_data.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="現在のパスワードが正しくありません"
            )
        
        # 新しいパスワード設定
        current_user.set_password(password_data.new_password)
        
        # 他のセッションを無効化（セキュリティ向上）
        session_manager.invalidate_user_sessions(db, current_user.id)
        
        db.commit()
        
        logger.info(f"パスワード変更: {current_user.username}")
        
        return {"message": "パスワードを変更しました。再度ログインしてください。"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"パスワード変更エラー: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="パスワード変更に失敗しました"
        )

@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """メール認証"""
    try:
        user = db.query(User).filter(
            User.email_verification_token == verification_data.token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無効な認証トークンです"
            )
        
        # メール認証完了
        user.is_verified = True
        user.email_verification_token = None
        db.commit()
        
        logger.info(f"メール認証完了: {user.username}")
        
        return {"message": "メール認証が完了しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"メール認証エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メール認証に失敗しました"
        )

@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """パスワードリセット要求"""
    try:
        user = db.query(User).filter(User.email == reset_data.email).first()
        
        if not user:
            # セキュリティ向上のため、存在しないメールアドレスでも成功レスポンス
            return {"message": "パスワードリセット用のメールを送信しました"}
        
        # リセットトークン生成
        reset_token = auth_manager.generate_reset_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1時間有効
        
        db.commit()
        
        # パスワードリセットメール送信（バックグラウンド）
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            reset_token,
            user.full_name or user.username
        )
        
        logger.info(f"パスワードリセット要求: {user.username}")
        
        return {"message": "パスワードリセット用のメールを送信しました"}
        
    except Exception as e:
        logger.error(f"パスワードリセット要求エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="パスワードリセット要求に失敗しました"
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """パスワードリセット実行"""
    try:
        user = db.query(User).filter(
            User.password_reset_token == reset_data.token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無効なリセットトークンです"
            )
        
        # トークン有効期限チェック
        if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="リセットトークンの有効期限が切れています"
            )
        
        # パスワード更新
        user.set_password(reset_data.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        # 全セッション無効化
        session_manager.invalidate_user_sessions(db, user.id)
        
        db.commit()
        
        logger.info(f"パスワードリセット完了: {user.username}")
        
        return {"message": "パスワードをリセットしました。新しいパスワードでログインしてください。"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"パスワードリセット実行エラー: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="パスワードリセットに失敗しました"
        )

@router.get("/sessions", response_model=list[SessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """ユーザーのアクティブセッション一覧"""
    try:
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).order_by(UserSession.last_accessed.desc()).all()
        
        # 現在のセッション特定（簡略版）
        session_responses = []
        for session in sessions:
            session_response = SessionResponse(
                id=session.id,
                device_info=session.device_info,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                is_active=session.is_active,
                expires_at=session.expires_at,
                created_at=session.created_at,
                last_accessed=session.last_accessed
            )
            session_responses.append(session_response)
        
        return session_responses
        
    except Exception as e:
        logger.error(f"セッション一覧取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッション一覧取得に失敗しました"
        )

@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """特定のセッション終了"""
    try:
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="セッションが見つかりません"
            )
        
        session.is_active = False
        db.commit()
        
        logger.info(f"セッション終了: ユーザー={current_user.username}, セッション={session_id}")
        
        return {"message": "セッションを終了しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"セッション終了エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッション終了に失敗しました"
        )

@router.get("/activity", response_model=list[ActivityLogResponse])
async def get_activity_log(
    limit: int = 50,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """ユーザーのアクティビティログ"""
    try:
        activities = db.query(ActivityLog).filter(
            ActivityLog.user_id == current_user.id
        ).order_by(ActivityLog.created_at.desc()).limit(limit).all()
        
        return activities
        
    except Exception as e:
        logger.error(f"アクティビティログ取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="アクティビティログ取得に失敗しました"
        )