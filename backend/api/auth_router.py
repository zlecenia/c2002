from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.db.base import get_db
from backend.auth.auth import (
    authenticate_user, 
    authenticate_user_qr, 
    create_access_token,
    get_current_user
)
from backend.models.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class QRLoginRequest(BaseModel):
    qr_code: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    email: Optional[str] = None

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with username and password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = create_access_token(subject=user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email
        }
    }

@router.post("/login/qr", response_model=Token)
def login_with_qr(
    qr_request: QRLoginRequest,
    db: Session = Depends(get_db)
):
    """Login with QR code."""
    user = authenticate_user_qr(db, qr_request.qr_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid QR code or inactive user"
        )
    
    access_token = create_access_token(subject=user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email
        }
    }

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "email": current_user.email
    }

@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    access_token = create_access_token(subject=current_user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }