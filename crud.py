from auth import get_password_hash
from database import execute_non_query, execute_query
from fastapi import HTTPException
from typing import Optional, List
from models import UserCreate

def create_user(user: UserCreate) -> int:
    hashed_password = get_password_hash(user.password)
    query = """
        INSERT INTO Users (Username, PasswordHash, Email, FirstName, LastName)
        VALUES (?, ?, ?, ?, ?)
    """
    params = (user.username, hashed_password, user.email, user.first_name, user.last_name)
    result = execute_non_query(query, params)
    # Get the new user's ID
    user_id = execute_query("SELECT UserId FROM Users WHERE Username = ?", (user.username,), fetch_one=True)
    if not user_id:
        raise HTTPException(status_code=500, detail="User creation failed")
    # Assign 'User' role
    assign_role_to_user(user_id[0], "User")
    return user_id[0]

def get_user_by_username(username: str) -> Optional[dict]:
    query = "SELECT UserId, Username, Email, FirstName, LastName, IsActive FROM Users WHERE Username = ?"
    user = execute_query(query, (username,), fetch_one=True)
    if user:
        return {
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
            "first_name": user[3],
            "last_name": user[4],
            "is_active": bool(user[5])
        }
    return None

def get_user_by_id(user_id: int) -> Optional[dict]:
    query = "SELECT UserId, Username, Email, FirstName, LastName, IsActive FROM Users WHERE UserId = ?"
    user = execute_query(query, (user_id,), fetch_one=True)
    if user:
        return {
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
            "first_name": user[3],
            "last_name": user[4],
            "is_active": bool(user[5])
        }
    return None

def get_user_roles(user_id: int) -> List[str]:
    query = """
        SELECT R.RoleName FROM UserRoles UR
        JOIN Roles R ON UR.RoleId = R.RoleId
        WHERE UR.UserId = ?
    """
    roles = execute_query(query, (user_id,), fetch_all=True)
    return [r[0] for r in roles] if roles else []

def assign_role_to_user(user_id: int, role_name: str):
    # Get RoleId
    role_id_query = "SELECT RoleId FROM Roles WHERE RoleName = ?"
    role_id = execute_query(role_id_query, (role_name,), fetch_one=True)
    if not role_id:
        raise HTTPException(status_code=404, detail="Role not found")
    # Assign role
    assign_query = "INSERT INTO UserRoles (UserId, RoleId) VALUES (?, ?)"
    try:
        execute_non_query(assign_query, (user_id, role_id[0]))
    except HTTPException as e:
        if e.status_code == 409:
            raise HTTPException(status_code=409, detail="User already has this role")
        raise

def authenticate_user(username: str, password: str) -> Optional[dict]:
    from auth import verify_password  # Moved import inside function
    user = get_user_by_username(username)
    if not user:
        return None
    query = "SELECT PasswordHash FROM Users WHERE Username = ?"
    result = execute_query(query, (username,), fetch_one=True)
    if result and verify_password(password, result[0]):
        return user
    return None

def update_user(user_id: int, user: UserCreate):
    query = """
        UPDATE Users SET Username = ?, Email = ?, FirstName = ?, LastName = ?, UpdatedAt = GETDATE()
        WHERE UserId = ?
    """
    params = (user.username, user.email, user.first_name, user.last_name, user_id)
    execute_non_query(query, params)

def delete_user(user_id: int):
    query = "DELETE FROM Users WHERE UserId = ?"
    execute_non_query(query, (user_id,))
