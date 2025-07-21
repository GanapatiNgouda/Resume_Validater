FastAPI User Authentication and Management Application Prompt
Generate a complete Python FastAPI application for user authentication and management, leveraging the provided SQL Server table schemas for Users, Roles, and UserRoles. The application should interact with a SQL Server database using pyodbc and implement JWT (JSON Web Token) for authentication.
Key Requirements:
1.	Project Structure:
Organize the code into logical files (e.g., main.py, database.py, models.py, auth.py, crud.py).
Use Pydantic for request and response models.
2.	Database Integration (pyodbc):
Define a database.py module to handle SQL Server connection pooling or management.
Implement functions to execute SQL queries (INSERT, SELECT, UPDATE, DELETE) against the Users, Roles, and UserRoles tables.
Ensure proper error handling for database operations.
Provide a placeholder for the SQL Server connection string.
3.	User Models (models.py):
UserCreate: Pydantic model for user registration (e.g., username, password, email, first_name, last_name).
UserLogin: Pydantic model for user login (e.g., username, password).
UserResponse: Pydantic model for user data returned to the client (exclude PasswordHash). Include roles.
Token: Pydantic model for JWT response (e.g., access_token, token_type).
RoleAssignment: Pydantic model for assigning roles to users (e.g., user_id, role_name).
4.	Password Hashing:
Use passlib.hash.bcrypt for secure password hashing and verification.
5.	JWT Authentication (auth.py):
Token Generation: A function to create JWT tokens upon successful user login, including user_id, username, and roles in the token payload.
Token Verification: A dependency function (Depends) to extract and verify JWT tokens from request headers, raising HTTPException for invalid or expired tokens.
Secret Key: Define a secure secret key for JWT signing (e.g., from environment variables).
Token Expiration: Set a reasonable expiration time for tokens.
6.	Authentication Endpoints (main.py):
POST /register: Allows new users to register. Hashes the password and saves the user to the Users table. Automatically assigns the 'User' role to new registrations.
POST /token: Authenticates a user based on username and password. If successful, returns a JWT access token.
7.	User Management Endpoints (user_endpoint.py):
GET /users/me: Returns details of the currently authenticated user.
GET /users/{user_id}: Returns details of a specific user by ID. (Admin-only)
PUT /users/{user_id}: Updates user details. (Admin or self-update)
DELETE /users/{user_id}: Deletes a user. (Admin-only)
8.	Role-Based Access Control (RBAC):
Implement a FastAPI dependency (Depends) to check user roles based on the decoded JWT token.
Apply this dependency to protect specific endpoints (e.g., /users/{user_id} for GET/PUT/DELETE, /roles/assign).
POST /roles/assign: Endpoint to assign a role to a user. (Admin-only)
9.	Error Handling:
Use FastAPI's HTTPException for various error scenarios (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict).
10.	Dependencies:
List all required Python packages in a requirements.txt format (e.g., fastapi, uvicorn, pyodbc, pydantic, python-jose[cryptography], passlib[bcrypt]).
Example SQL Interactions (within the Python code):
Register User: INSERT INTO Users (Username, PasswordHash, Email, ...) VALUES (?, ?, ?, ...)
Login User: SELECT UserId, Username, PasswordHash FROM Users WHERE Username = ?
Get User Roles: SELECT R.RoleName FROM UserRoles UR JOIN Roles R ON UR.RoleId = R.RoleId WHERE UR.UserId = ?
Assign Role: INSERT INTO UserRoles (UserId, RoleId) VALUES (?, (SELECT RoleId FROM Roles WHERE RoleName = ?))
Provide complete, runnable code for all components.