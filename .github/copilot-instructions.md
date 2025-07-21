

Project Goal: Generate a complete Python FastAPI application for user authentication and management. It should interact with a SQL Server database (using `pyodbc`), implement JWT for authentication, and feature role-based access control.

## Core Requirements & Structure:

1.  Project Files:
    * `main.py`: Main FastAPI application, routing, and endpoint definitions.
    * `database.py`: SQL Server connection, query execution, and error handling.
    * `models.py`: Pydantic models for request/response bodies and JWT tokens.
    * `auth.py`: JWT token generation, verification, and authentication dependencies.
    * `crud.py`: Database interaction functions for Users, Roles, and UserRoles.

2.  **Database (SQL Server with `pyodbc`):**
    * Define a placeholder connection string.
    * Implement functions for `SELECT`, `INSERT`, `UPDATE`, `DELETE` operations.
    * Ensure robust error handling for database operations.
    * Reusable functions mentioned in `database.py`


3.  **Role-Based Access Control (RBAC):**
    * Create `Depends` functions in `auth.py` to check for specific roles (e.g., `get_current_admin_user`).
    * Apply these dependencies to protected endpoints.
    * `POST /roles/assign`: Endpoint to assign a role to a user (`RoleAssignment`). **Requires 'Admin' role.**

4.  **Error Handling:**
    * Utilize FastAPI's `HTTPException` (e.g., `400`, `401`, `403`, `404`, `409`).

5. **Dependencies (`requirements.txt`):**
    * `fastapi`
    * `uvicorn`
    * `pyodbc`
    * `pydantic`
    * `python-jose[cryptography]`
    * `passlib[bcrypt]`


