"""
Authentication and JWT token management
"""
import os
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

try:
    from fastapi import HTTPException, status
except ImportError:
    # FastAPI not available - CLI mode
    HTTPException = None
    status = None

from ..models.user import User


class TokenData(BaseModel):
    """Token payload data"""
    username: str | None = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class AuthConfig:
    """Authentication configuration"""

    def __init__(self) -> None:
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# Global auth configuration
auth_config = AuthConfig()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    result: Any = pwd_context.verify(plain_password, hashed_password)
    return bool(result)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    result: Any = pwd_context.hash(password)
    return str(result)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_config.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt: Any = jwt.encode(to_encode, auth_config.secret_key, algorithm=auth_config.algorithm)
    return str(encoded_jwt)


def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """Verify JWT token and extract user data"""
    try:
        payload = jwt.decode(token, auth_config.secret_key, algorithms=[auth_config.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e


def validate_password_strength(password: str) -> bool:
    """Validate password meets strength requirements"""
    # At least 8 characters, contains uppercase, lowercase, digit, and special char
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    return has_upper and has_lower and has_digit and has_special


def authenticate_user(email: str, password: str, user: User | None) -> User | bool:
    """Authenticate user with email and password"""
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
