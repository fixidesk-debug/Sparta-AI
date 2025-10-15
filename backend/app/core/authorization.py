from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def require_permission(permission: str):
    """FastAPI dependency factory to require a permission on the current user."""

    def _require(user: User = Depends(get_current_user)):
        # Expecting User model to implement `has_permission(permission)` method
        has_perm = getattr(user, 'has_permission', None)
        if callable(has_perm):
            if not has_perm(permission):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        else:
            # If no permissions support, default to allowing but log
            # To be strict, you could deny by default here instead.
            return user
        return user

    return _require
