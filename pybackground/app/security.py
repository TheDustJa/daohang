from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Header, HTTPException, status

from .config import ACCESS_TOKEN_EXPIRE_HOURS, SECRET_KEY
from .repositories import get_admin_by_username
from .utils import password_hash


def create_access_token(username: str) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": username, "exp": expire_at}, SECRET_KEY, algorithm="HS256")


def verify_admin_password(username: str, password: str) -> bool:
    admin = get_admin_by_username(username)
    if admin is None:
      return False
    return admin["passwordHash"] == password_hash(password)


def require_admin_token(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization[len("Bearer "):].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    username = payload.get("sub")
    if not username or get_admin_by_username(username) is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return username
