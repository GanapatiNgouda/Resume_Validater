from fastapi import APIRouter, Depends, HTTPException
from models import UserCreate, UserResponse
from crud import get_user_by_id, update_user, delete_user, get_user_roles
from auth import get_current_user, get_current_admin_user

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: UserResponse = Depends(get_current_admin_user)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roles = get_user_roles(user_id)
    return UserResponse(**user, roles=roles)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_details(user_id: int, user: UserCreate, current_user: UserResponse = Depends(get_current_user)):
    if current_user.user_id != user_id and "Admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    update_user(user_id, user)
    user_data = get_user_by_id(user_id)
    roles = get_user_roles(user_id)
    return UserResponse(**user_data, roles=roles)

@router.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int, current_user: UserResponse = Depends(get_current_admin_user)):
    delete_user(user_id)
    return {"detail": "User deleted"}
