# AI Workspace V2 — Database Architecture

## 1. Database

PostgreSQL

## 2. Tables

### users
### user_sessions
### workspaces
### workspace_members
### projects
### project_members

## 3. Relationships

## 4. Foreign Keys

## 5. Cascades

## 6. Composite Keys

## 7. Enums

## 8. Migration History

## 9. Current Schema Drift




User
 │
 ├──< UserSession
 │
 ├──< Workspace
 │       │
 │       ├──< WorkspaceMember >── User
 │       │
 │       └──< Project
 │               │
 │               └──< ProjectMember >── User
 │
 └──< Project (created_by)





 Revision	    Purpose	                            Depends On
b897b8c6500d	Users + sessions	                    —
611f8a4c7a08	Workspaces	                        Initial schema
b89fc110ebbe	Projects	                        Workspaces
15f71f06347e	Workspace members	                Projects
888bb361507a	Project members + owner backfill	Workspace members



Existing project creators are backfilled as PROJECT OWNER
members.

projects.created_by
        ↓
project_members
        ↓
role = OWNER




## Current Schema Drift

The current SQLAlchemy models and PostgreSQL migrations are not
completely synchronized.

### 1. WorkspaceMember.invited_by

Model:
    invited_by exists

Migration:
    invited_by does not exist

Status:
    Needs migration/model reconciliation

### 2. Project.visibility

Database:
    visibility exists

Model:
    visibility is not currently represented

Status:
    Needs product/design decision

### 3. User.full_name

Model:
    VARCHAR(120)

Database:
    VARCHAR(100)

Status:
    Mismatch

### 4. User.avatar_url

Model:
    VARCHAR(500)

Database:
    VARCHAR(255)

Status:
    Mismatch

### 5. User.is_active / is_verified

Database:
    nullable

Application:
    treated as boolean state

Status:
    Needs schema hardening

### 6. Project.status

Application:
    ProjectStatus enum

Database:
    VARCHAR(20)

Status:
    Application-level enum, database-level string