from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.base import get_db
from backend.models.models import User
import secrets
import string

# Security scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(
    subject: Union[str, Any], 
    roles: Optional[list] = None,
    active_role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token with roles support."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "roles": roles or [],
        "active_role": active_role
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload with username, roles, and active_role."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username = payload.get("sub")
        if username is None:
            return None
        return {
            "username": str(username),
            "roles": payload.get("roles", []),
            "active_role": payload.get("active_role")
        }
    except JWTError:
        return None

def generate_qr_code() -> str:
    """Generate a unique QR code."""
    return "QR" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, str(user.password_hash)):
        return None
    return user

def authenticate_user_qr(db: Session, qr_code: str) -> Optional[User]:
    """Authenticate a user with QR code."""
    user = db.query(User).filter(User.qr_code == qr_code).first()
    if not user or user.is_active is False:
        return None
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data["username"]).first()
    if user is None:
        raise credentials_exception
    
    # Attach token roles and active_role to user object for request context
    user.token_roles = token_data.get("roles", [])
    user.token_active_role = token_data.get("active_role")
    
    return user

def require_role(required_role: str):
    """Decorator to require specific user role. Checks active_role from token."""
    def role_checker(current_user: User = Depends(get_current_user)):
        # Get active role from token (set in get_current_user)
        active_role = getattr(current_user, 'token_active_role', None) or str(current_user.role)
        user_roles = getattr(current_user, 'token_roles', [])
        if not user_roles:
            user_roles = []
        
        # Allow if active role matches required role, or if user is superuser, or if required role is in user's roles
        if (str(active_role) == str(required_role) or 
            str(active_role) == "superuser" or 
            str(required_role) in [str(r) for r in user_roles]):
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. Required role: {required_role}, Active role: {active_role}"
        )
    return role_checker