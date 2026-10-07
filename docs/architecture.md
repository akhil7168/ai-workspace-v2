# AI Workspace V2 — Backend Architecture

## 1. Overview

## 2. Architecture Style

## 3. Project Structure

## 4. Request Lifecycle

## 5. Authentication Architecture

## 6. Authorization Architecture

### 6.1 Global Roles
### 6.2 Workspace Roles
### 6.3 Project Roles
### 6.4 Project Ownership

## 7. Service Layer

## 8. Repository Layer

## 9. Database Access

## 10. Migration Architecture

## 11. Current Architectural Issues

## 12. Planned Improvements




Current architectural inconsistencies:
- Two SQLAlchemy engine definitions exist.
- Two Base definitions exist.
- Two authentication dependency implementations exist.
- Repository/service database parameters use Any rather than Session.
- Some authorization paths use project ownership while others use project membership.





## Authentication Flow

Client
  ↓
Authorization: Bearer <JWT>
  ↓
OAuth2PasswordBearer
  ↓
JWT decode
  ↓
Extract `sub`
  ↓
Convert `sub` to UUID
  ↓
Query users table
  ↓
Current User
  ↓
Optional active-user validation




Login
 ↓
Access Token
 +
Refresh Token
 ↓
Refresh Token stored in user_sessions
 ↓
Client uses access token
 ↓
Access token expires
 ↓
Refresh token checked against session
 ↓
New token pair



Logout
 ↓
Refresh-token session revoked
 ↓
is_revoked = true



For workspace operations :

Request
 ↓
JWT authentication
 ↓
Current user
 ↓
Find WorkspaceMember
 ↓
Get WorkspaceRole
 ↓
PermissionService
 ↓
ROLE_PERMISSIONS
 ↓
Allow / 403


For project membership :

Request
 ↓
JWT authentication
 ↓
Find Project
 ↓
Find WorkspaceMember
 ↓
Find ProjectMember
 ↓
ProjectRole
 ↓
PROJECT_ROLE_PERMISSIONS
 ↓
Allow / 403


For project ownership : 


Request
 ↓
Current User
 ↓
Project
 ↓
project.created_by == current_user.id
 ↓
Allow / 403


