import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import jwt
import bcrypt
from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app.models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "pocketsmart_ai_super_secret_jwt_key_2025_college_demo_secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def hash_password(password: str) -> str:
    """Securely hash a password using bcrypt."""
    try:
        # Convert password to bytes and hash with salt
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')
    except Exception:
        # Fallback to PBKDF2 with SHA256 if bcrypt encounters any environmental issue
        salt = os.urandom(16)
        kdf = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return f"pbkdf2:{salt.hex()}:{kdf.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash or fallback pbkdf2 hash."""
    try:
        if hashed_password.startswith("pbkdf2:"):
            _, salt_hex, hash_hex = hashed_password.split(":")
            salt = bytes.fromhex(salt_hex)
            test_kdf = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
            return hmac.compare_digest(test_kdf.hex(), hash_hex)

        pwd_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header or 'access_token' cookie."""
    # Check Authorization header: 'Bearer <token>'
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    # Check cookies
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            return cookie_token.split(" ")[1]
        return cookie_token

    return None


def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    """Decode token and retrieve user from database."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except (jwt.PyJWTError, ValueError, KeyError):
        return None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """FastAPI dependency: requires a valid authenticated user or raises HTTP 401."""
    token = extract_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_current_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_optional_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """FastAPI dependency: returns the User if authenticated, else None (safe for public pages)."""
    token = extract_token(request)
    if not token:
        return None
    return get_current_user_from_token(token, db)
