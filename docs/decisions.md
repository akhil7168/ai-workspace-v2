# Architecture Decisions

## ADR-001 — Layered Backend Architecture

Decision:
Use Router → Service → Repository → Database layering.

Reason:
Keep API concerns, business logic and persistence concerns separated.

Status:
Accepted


### ADR-002 — Server-side refresh-token sessions

Decision:
Persist refresh-token sessions in PostgreSQL.

Reason:
Allows server-side session revocation and logout.

Status:
Accepted


### ADR-003 — Separate workspace and project RBAC

Decision:
Workspace roles and project roles are separate authorization systems.

Reason:
Project access needs finer-grained control than workspace membership.

Status:
Accepted


### ADR-004 — Project creator ownership

Decision:
Project ownership is represented by projects.created_by.

Status:
Accepted for current architecture.

Future:
Evaluate relationship with ProjectMember OWNER role.

### ADR-005 — Known schema drift

Decision:
Do not silently modify the database during architecture audit.

Reason:
Schema changes will be handled through deliberate migrations
after model/service/test reconciliation.

Status:
Planned

### High Priority

TD-001 Duplicate SQLAlchemy engines
TD-002 Duplicate Base definitions
TD-003 Duplicate authentication implementations
TD-004 WorkspaceMember.invited_by model/migration mismatch
TD-005 Project.visibility model/migration mismatch
TD-006 User length mismatches
TD-007 Review project authorization coverage

### Medium Priority 

TD-008 Nullable user state columns
TD-009 Project status database constraint
TD-010 Workspace owner membership invariant
TD-011 Project ownership vs ProjectMember OWNER duplication


### Low Priority

TD-012 Repository `Any` → Session typing
TD-013 Enum naming consistency
TD-014 Constraint naming
TD-015 Remove unused imports
TD-016 Repository/service dependency construction


