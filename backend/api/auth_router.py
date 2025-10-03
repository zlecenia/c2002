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
    get_current_user,
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
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Get user roles - use roles JSON column or fall back to single role
    user_roles_data = user.roles
    if (
        user_roles_data is not None
        and isinstance(user_roles_data, list)
        and len(user_roles_data) > 0
    ):
        user_roles = user_roles_data
    else:
        user_roles = [str(user.role)]
    active_role = str(user.role)  # Default active role is the primary role

    access_token = create_access_token(
        subject=user.username, roles=user_roles, active_role=active_role
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "roles": user_roles,
            "active_role": active_role,
            "email": user.email,
        },
    }


@router.post("/login/qr", response_model=Token)
def login_with_qr(qr_request: QRLoginRequest, db: Session = Depends(get_db)):
    """Login with QR code."""
    user = authenticate_user_qr(db, qr_request.qr_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid QR code or inactive user"
        )

    # Get user roles - use roles JSON column or fall back to single role
    user_roles_data = user.roles
    if (
        user_roles_data is not None
        and isinstance(user_roles_data, list)
        and len(user_roles_data) > 0
    ):
        user_roles = user_roles_data
    else:
        user_roles = [str(user.role)]
    active_role = str(user.role)  # Default active role is the primary role

    access_token = create_access_token(
        subject=user.username, roles=user_roles, active_role=active_role
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "roles": user_roles,
            "active_role": active_role,
            "email": user.email,
        },
    }


@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information, including roles from token."""
    roles = getattr(current_user, "token_roles", []) or []
    active_role = getattr(current_user, "token_active_role", None) or str(current_user.role)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": str(current_user.role),
        "roles": roles,
        "active_role": active_role,
        "email": current_user.email,
    }


@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    # Get user roles - use roles JSON column or fall back to single role
    user_roles_data = current_user.roles
    if (
        user_roles_data is not None
        and isinstance(user_roles_data, list)
        and len(user_roles_data) > 0
    ):
        user_roles = user_roles_data
    else:
        user_roles = [str(current_user.role)]
    active_role = getattr(current_user, "token_active_role", None) or str(current_user.role)

    access_token = create_access_token(
        subject=current_user.username, roles=user_roles, active_role=active_role
    )
    return {"access_token": access_token, "token_type": "bearer"}


class SwitchRoleRequest(BaseModel):
    new_role: str


@router.post("/switch-role", response_model=Token)
def switch_role(role_request: SwitchRoleRequest, current_user: User = Depends(get_current_user)):
    """Switch active role without re-login."""
    # Get user's available roles
    user_roles_data = current_user.roles
    if (
        user_roles_data is not None
        and isinstance(user_roles_data, list)
        and len(user_roles_data) > 0
    ):
        user_roles = user_roles_data
    else:
        user_roles = [str(current_user.role)]

    # Verify the requested role is available to the user
    if role_request.new_role not in user_roles and role_request.new_role != str(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role_request.new_role}' not available. Available roles: {', '.join(user_roles)}",
        )

    # Create new token with the new active role
    access_token = create_access_token(
        subject=current_user.username, roles=user_roles, active_role=role_request.new_role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "roles": user_roles,
            "active_role": role_request.new_role,
            "email": current_user.email,
        },
    }
