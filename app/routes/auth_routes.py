from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreate
from app.auth import (
    verify_password,
    hash_password,
    create_access_token,
    create_expired_token,
    get_current_user
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT access token."""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600,
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )

    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role or "customer"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "username": new_user.username, "role": new_user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600,
        user_id=new_user.id,
        username=new_user.username,
        role=new_user.role
    )


@router.post("/expired-token-simulate")
def generate_expired_token(request: LoginRequest, db: Session = Depends(get_db)):
    """SDET utility endpoint: generates an expired JWT token for negative auth testing."""
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    token = create_expired_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"expired_token": token, "expires_in": -7200}


@router.get("/me")
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Protected endpoint to verify current user session and token claims."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat()
    }
