from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.db.base import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerification,
)
from app.models.user import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    validate_password_strength,
    generate_verification_token,
    generate_reset_token,
)
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.core.rate_limit import rate_limiter
from app.services.email import email_service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email verification."""
    # Rate limiting
    await rate_limiter.check_rate_limit(request)

    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Generate verification token
    verification_token = generate_verification_token()

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email, password_hash=hashed_password, verification_token=verification_token, is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    try:
        email_service.send_verification_email(user_data.email, verification_token)
    except Exception as e:
        print(f"Failed to send verification email: {e}")

    return new_user


@router.post("/login", response_model=Token)
async def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access and refresh tokens."""
    # Rate limiting
    await rate_limiter.check_rate_limit(request)

    # Find user
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    # Rate limiting
    await rate_limiter.check_rate_limit(request)

    # Decode refresh token
    payload = decode_access_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Verify user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-email")
async def verify_email(verification_data: EmailVerification, db: Session = Depends(get_db)):
    """Verify user email address."""
    user = db.query(User).filter(User.verification_token == verification_data.token).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

    user.is_verified = True
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(request: Request, reset_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset."""
    # Rate limiting
    await rate_limiter.check_rate_limit(request)

    user = db.query(User).filter(User.email == reset_data.email).first()

    # Don't reveal if user exists or not
    if user:
        # Generate reset token
        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        # Send reset email
        try:
            email_service.send_password_reset_email(user.email, reset_token)
        except Exception as e:
            print(f"Failed to send reset email: {e}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: Request, reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using token."""
    # Rate limiting
    await rate_limiter.check_rate_limit(request)

    # Validate new password strength
    is_valid, error_message = validate_password_strength(reset_data.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    user = db.query(User).filter(User.reset_token == reset_data.token).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

    # Check if token expired
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired")

    # Update password
    user.password_hash = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password reset successfully"}
