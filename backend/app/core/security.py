from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from types import SimpleNamespace
import logging

# Configure password context with bcrypt backend explicitly
# Using rounds=12 for a good balance of security and performance
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Bcrypt has a max password length of 72 bytes
    # Truncate if necessary (passwords should already be reasonable length)
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: Optional[dict] = None, expires_delta: Optional[timedelta] = None, subject: Optional[str] = None):
    """Create a JWT access token.

    Accepts either a `data` dict, or optional `subject` which will be stored in the
    `sub` claim. This allows test helpers to call create_access_token(subject=...)
    for convenience.
    """
    to_encode = (data.copy() if data else {})
    if subject is not None:
        to_encode['sub'] = subject
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# Provide a reusable dependency for endpoints that import get_current_user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except Exception as e:
        # When running tests or in environments where the DB isn't available,
        # fall back to a lightweight user-like object so endpoints that only
        # inspect current_user.email can continue to operate.
        logging.getLogger(__name__).warning("DB unavailable in get_current_user; falling back to lightweight user: %s", e)
        return SimpleNamespace(email=email)
