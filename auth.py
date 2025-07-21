from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
import os
from crud import get_user_by_username, get_user_roles
from models import UserResponse

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username)
    if not user:
        raise credentials_exception
    roles = get_user_roles(user["user_id"])
    return UserResponse(
        user_id=user["user_id"],
        username=user["username"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        is_active=user["is_active"],
        roles=roles
    )

def get_current_admin_user(current_user: UserResponse = Depends(get_current_user)):
    if "Admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def get_current_moderator_user(current_user: UserResponse = Depends(get_current_user)):
    if "Moderator" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Moderator privileges required")
    return current_user
