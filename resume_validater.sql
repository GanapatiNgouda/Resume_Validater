-- Database creation

create database resume_validater;
use resume_validater;

-- Create the Roles table

CREATE TABLE Roles (
    RoleId INT PRIMARY KEY IDENTITY(1,1), -- Unique identifier for the role
    RoleName NVARCHAR(50) NOT NULL UNIQUE, -- Name of the role (e.g., 'User', 'Admin')
    Description NVARCHAR(255) NULL,       -- Optional description for the role
    CreatedAt DATETIME DEFAULT GETDATE(), -- Timestamp for when the role was created
    UpdatedAt DATETIME DEFAULT GETDATE()  -- Timestamp for when the role was last updated
);

-- Create the Users table
CREATE TABLE Users (
    UserId INT PRIMARY KEY IDENTITY(1,1),    -- Unique identifier for the user
    Username NVARCHAR(100) NOT NULL UNIQUE, -- User's chosen username (must be unique)
    PasswordHash NVARCHAR(255) NOT NULL,    -- Hashed password for security
    Email NVARCHAR(255) UNIQUE,              -- User's email address (optional, but good for recovery)
    FirstName NVARCHAR(100) NULL,            -- User's first name
    LastName NVARCHAR(100) NULL,             -- User's last name
    IsActive BIT DEFAULT 1,                  -- Flag to indicate if the user account is active
    CreatedAt DATETIME DEFAULT GETDATE(),    -- Timestamp for when the user was created
    UpdatedAt DATETIME DEFAULT GETDATE()     -- Timestamp for when the user was last updated
);

-- Create the UserRoles linking table for many-to-many relationship
CREATE TABLE UserRoles (
    UserRoleId INT PRIMARY KEY IDENTITY(1,1), -- Unique identifier for the linking entry
    UserId INT NOT NULL,                      -- Foreign key referencing the Users table
    RoleId INT NOT NULL,                      -- Foreign key referencing the Roles table
    AssignedAt DATETIME DEFAULT GETDATE(),    -- Timestamp for when the role was assigned

    -- Define foreign key constraints
    CONSTRAINT FK_UserRoles_Users FOREIGN KEY (UserId) REFERENCES Users(UserId) ON DELETE CASCADE,
    CONSTRAINT FK_UserRoles_Roles FOREIGN KEY (RoleId) REFERENCES Roles(RoleId) ON DELETE CASCADE,

    -- Ensure a user can only have a specific role assigned once
    CONSTRAINT UQ_UserRoles UNIQUE (UserId, RoleId)
);

-- Optional: Insert some initial roles
INSERT INTO Roles (RoleName, Description) VALUES
('Admin', 'Administrator with full system access'),
('User', 'Standard user with basic application access'),
('Moderator', 'Content moderator with specific permissions');

-- Optional: Add indexes for performance on frequently queried columns
CREATE INDEX IX_Users_Username ON Users (Username);
CREATE INDEX IX_Users_Email ON Users (Email);
CREATE INDEX IX_UserRoles_UserId ON UserRoles (UserId);
CREATE INDEX IX_UserRoles_RoleId ON UserRoles (RoleId);
