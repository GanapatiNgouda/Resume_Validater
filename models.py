from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    roles: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class RoleAssignment(BaseModel):
    user_id: int
    role_name: str
