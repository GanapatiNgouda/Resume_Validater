from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import UserCreate, Token, RoleAssignment, UserResponse
from crud import create_user, authenticate_user, assign_role_to_user, get_user_by_id, get_user_roles
from auth import create_access_token, get_current_admin_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    user_id = create_user(user)
    user_data = get_user_by_id(user_id)
    roles = get_user_roles(user_id)
    return UserResponse(**user_data, roles=roles)

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    roles = get_user_roles(user["user_id"])
    access_token = create_access_token({
        "user_id": user["user_id"],
        "username": user["username"],
        "roles": roles
    })
    return Token(access_token=access_token, token_type="bearer")

@router.post("/roles/assign")
def assign_role(role: RoleAssignment, current_user: UserResponse = Depends(get_current_admin_user)):
    assign_role_to_user(role.user_id, role.role_name)
    return {"detail": f"Role '{role.role_name}' assigned to user {role.user_id}"}
