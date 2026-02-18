from fastapi import APIRouter, HTTPException, Depends, Response, Request
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta
from secrets import token_urlsafe

from app.database import get_session
from app.models import User, RefreshToken, PasswordResetToken, RoleEnum
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter(prefix="/auth", tags=["auth"])


# Request/Response schemas
class RegisterRequest(BaseModel):
    """Registration request"""
    name: str
    email: EmailStr
    password: str
    role: str
    org_name: str


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RefreshResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User profile response"""
    id: int
    name: str
    email: str
    role: str
    org_name: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str


@router.post("/register", response_model=dict, summary="Register new user")
def register(
    payload: RegisterRequest,
    session: Session = Depends(get_session)
):
    """Register a new user"""
    # Check if user already exists
    existing = session.exec(
        select(User).where(User.email == payload.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=RoleEnum(payload.role),
        org_name=payload.org_name
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "org_name": user.org_name,
        "message": "User registered successfully"
    }


@router.post("/login", response_model=LoginResponse, summary="Login user")
def login(
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    """Login user and return JWT tokens"""
    # Find user by email
    user = session.exec(
        select(User).where(User.email == payload.email)
    ).first()
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    refresh_token = create_refresh_token(
        user_id=user.id,
        email=user.email
    )
    
    # Store refresh token hash in database
    token_hash = hash_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    rt = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    session.add(rt)
    session.commit()
    
    # Set refresh token in HTTPOnly cookie
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7*24*60*60  # 7 days
    )
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "org_name": user.org_name
        }
    )


@router.post("/refresh", response_model=RefreshResponse, summary="Refresh access token")
def refresh(
    request: Request,
    session: Session = Depends(get_session)
):
    """Refresh access token using refresh token from cookie"""
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refreshToken")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    # Verify token
    token_data = verify_token(refresh_token)
    if not token_data or token_data.token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Check if token is in database and not revoked
    token_hash = hash_token(refresh_token)
    rt = session.exec(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        )
    ).first()
    
    if not rt or rt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")
    
    # Create new access token
    user = session.exec(select(User).where(User.id == token_data.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    return RefreshResponse(access_token=new_access_token)


@router.get("/user", response_model=UserResponse, summary="Get current user")
def get_user(
    authorization: str = None,
    session: Session = Depends(get_session)
):
    """Get current user profile"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # Verify token
    token_data = verify_token(token)
    if not token_data or token_data.token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Fetch user
    user = session.exec(select(User).where(User.id == token_data.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        org_name=user.org_name
    )


@router.post("/logout", summary="Logout user")
def logout(response: Response):
    """Logout user by clearing refresh token cookie"""
    response.delete_cookie("refreshToken")
    return {"message": "Logged out successfully"}


@router.post("/forgot-password", summary="Request password reset")
def forgot_password(
    payload: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    """Request password reset - generates reset token and sends email"""
    user = session.exec(
        select(User).where(User.email == payload.email)
    ).first()
    
    if not user:
        # For security, don't reveal if email exists
        return {
            "message": "If an account exists with that email, a reset link has been sent."
        }
    
    # Generate reset token
    reset_token = token_urlsafe(32)
    token_hash = hash_token(reset_token)
    
    # Store reset token (expires in 24 hours)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    reset_token_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    session.add(reset_token_record)
    session.commit()
    
    # In production, send email with reset link like:
    # reset_url = f"https://yourapp.com/reset-password?token={reset_token}"
    # send_email(user.email, reset_url)
    
    # For demo, we'll return the token (NOT for production!)
    # In production, only send via email
    print(f"[DEV MODE] Password reset token for {user.email}: {reset_token}")
    
    return {
        "message": "If an account exists with that email, a reset link has been sent.",
        "reset_token": reset_token  # Remove in production!
    }


@router.post("/reset-password", summary="Reset password with token")
def reset_password(
    payload: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    """Reset password using reset token"""
    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )
    
    # Find reset token by hash
    token_hash = hash_token(payload.token)
    reset_token = session.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
    ).first()
    
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    # Check if token is expired
    if datetime.now(timezone.utc) > reset_token.expires_at:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Check if token was already used
    if reset_token.is_used:
        raise HTTPException(status_code=400, detail="Reset token has already been used")
    
    # Get user
    user = session.exec(
        select(User).where(User.id == reset_token.user_id)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = datetime.now(timezone.utc)
    
    # Mark token as used
    reset_token.is_used = True
    
    session.add(user)
    session.add(reset_token)
    session.commit()
    
    return {"message": "Password reset successfully"}
