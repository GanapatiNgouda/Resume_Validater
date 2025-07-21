3.  **User Models (`models.py`):**
    * `UserCreate`: `username`, `password`, `email`, `first_name`, `last_name`.
    * `UserLogin`: `username`, `password`.
    * `UserResponse`: `user_id`, `username`, `email`, `first_name`, `last_name`, `is_active`, `roles` (list of strings). **Exclude `PasswordHash`**.
    * `Token`: `access_token`, `token_type`.
    * `RoleAssignment`: `user_id`, `role_name`.

4.  **Password Hashing:**
    * Use `passlib.hash.bcrypt` for hashing and verification.

5.  **JWT Authentication (`auth.py`):**
    * **Token Generation:** Function to create JWTs with `user_id`, `username`, and `roles` in the payload.
    * **Token Verification:** FastAPI `Depends` function to extract, decode, and validate tokens from headers. Raise `HTTPException` for issues.
    * **Secret Key:** Use an environment variable or a placeholder.
    * **Expiration:** Set a reasonable token expiration (e.g., 30 minutes).

6.  **Authentication Endpoints (`main.py`):**
    * `POST /register`:
        * Accepts `UserCreate` data.
        * Hashes password.
        * Inserts user into `Users` table.
        * Automatically assigns the 'User' role to new registrations.
        * Handles `409 Conflict` for duplicate usernames/emails.
    * `POST /token`:
        * Accepts `UserLogin` data.
        * Authenticates username/password.
        * Returns `Token` (JWT access token) on success.
        * Handles `401 Unauthorized` for invalid credentials.

7.  **User Management Endpoints (`main.py` - can be integrated or in a separate router):**
    * `GET /users/me`: Returns details of the currently authenticated user (`UserResponse`).
    * `GET /users/{user_id}`: Returns details of a specific user. **Requires 'Admin' role.**
    * `PUT /users/{user_id}`: Updates user details. **Requires 'Admin' role or self-update.**
    * `DELETE /users/{user_id}`: Deletes a user. **Requires 'Admin' role.**
