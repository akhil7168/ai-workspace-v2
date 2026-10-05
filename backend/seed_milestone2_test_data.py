from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import hash_password

from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.models.project_member import ProjectMember, ProjectRole


# ============================================================
# TEST USERS
# ============================================================

USERS = {
    "akhil@example.com": {
        "global_role": "user",
        "password": "Akhil@123",
    },
    "Akhiladmin@example.com": {
        "global_role": "admin",
        "password": "Admin@123",
    },
    "milestone2@example.com": {
        "global_role": "user",
        "password": "Member@123",
    },
    "Viewer@example.com": {
        "global_role": "user",
        "password": "Viewer@123",
    },
    "session_test@example.com": {
        "global_role": "user",
        "password": "SessionTest@123",
    },
    "rotation_test@example.com": {
        "global_role": "user",
        "password": "RotationTest@123",
    },
    "logout_test@example.com": {
        "global_role": "user",
        "password": "LogoutTest@123",
    },
}


# ============================================================
# INDIVIDUAL USER RESOURCES
# ============================================================

INDIVIDUAL_RESOURCES = {
    "akhil@example.com": (
        "M2 Akhil Workspace",
        "M2 Akhil Project",
    ),

    "Akhiladmin@example.com": (
        "M2 AkhilAdmin Workspace",
        "M2 AkhilAdmin Project",
    ),

    "milestone2@example.com": (
        "M2 Milestone2 Workspace",
        "M2 Milestone2 Project",
    ),

    "Viewer@example.com": (
        "M2 Viewer Workspace",
        "M2 Viewer Project",
    ),

    "session_test@example.com": (
        "M2 Session Workspace",
        "M2 Session Project",
    ),

    "rotation_test@example.com": (
        "M2 Rotation Workspace",
        "M2 Rotation Project",
    ),

    "logout_test@example.com": (
        "M2 Logout Workspace",
        "M2 Logout Project",
    ),
}


# ============================================================
# SHARED SPRINT 7 LAB
# ============================================================

LAB_WORKSPACE_NAME = "M2 Sprint7 Lab Workspace"
LAB_PROJECT_NAME = "M2 Sprint7 Lab Project"


LAB_WORKSPACE_ROLES = {
    "akhil@example.com": WorkspaceRole.OWNER,
    "Akhiladmin@example.com": WorkspaceRole.ADMIN,
    "milestone2@example.com": WorkspaceRole.MEMBER,
    "Viewer@example.com": WorkspaceRole.VIEWER,
    "session_test@example.com": WorkspaceRole.MEMBER,
    "rotation_test@example.com": WorkspaceRole.MEMBER,
    "logout_test@example.com": WorkspaceRole.MEMBER,
}


LAB_PROJECT_ROLES = {
    "akhil@example.com": ProjectRole.OWNER,
    "Akhiladmin@example.com": ProjectRole.ADMIN,
    "milestone2@example.com": ProjectRole.MEMBER,
    "Viewer@example.com": ProjectRole.VIEWER,
}


# ============================================================
# HELPERS
# ============================================================

def get_user(db: Session, email: str) -> User:
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise RuntimeError(
            f"User not found: {email}"
        )

    return user


def get_or_create_workspace(
    db: Session,
    user: User,
    name: str,
) -> Workspace:

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.name == name,
            Workspace.owner_id == user.id,
        )
        .first()
    )

    if workspace is None:
        workspace = Workspace(
            owner_id=user.id,
            name=name,
            description=f"Milestone 2 test workspace for {user.email}",
        )

        db.add(workspace)
        db.flush()

    return workspace


def get_or_create_project(
    db: Session,
    workspace: Workspace,
    user: User,
    title: str,
) -> Project:

    project = (
        db.query(Project)
        .filter(
            Project.workspace_id == workspace.id,
            Project.title == title,
        )
        .first()
    )

    if project is None:
        project = Project(
            title=title,
            description=f"Milestone 2 test project for {user.email}",
            workspace_id=workspace.id,
            created_by=user.id,
        )

        db.add(project)
        db.flush()

    return project


def ensure_workspace_membership(
    db: Session,
    workspace_id,
    user_id,
    role: WorkspaceRole,
):

    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )

    if membership is None:

        membership = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )

        db.add(membership)

    else:
        membership.role = role

    db.flush()

    return membership


def ensure_project_membership(
    db: Session,
    project_id,
    user_id,
    role: ProjectRole,
):

    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )

    if membership is None:

        membership = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
            assigned_by=user_id,
        )

        db.add(membership)

    else:
        membership.role = role

    db.flush()

    return membership


# ============================================================
# SEED
# ============================================================

def main():

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 1. Validate users
        # ----------------------------------------------------

        users = {}

        for email, config in USERS.items():

            user = get_user(
                db,
                email,
            )

            users[email] = user

            # Keep User.role aligned with the actual model:
            # only "user" / "admin"
            user.role = config["global_role"]

            # Reset known test passwords
            user.password_hash = hash_password(
                config["password"]
            )

        db.flush()

        print("\nUSERS READY")
        print("=" * 70)

        for email, user in users.items():

            print(
                f"{email:<32} "
                f"{user.id} "
                f"global_role={user.role}"
            )

        # ----------------------------------------------------
        # 2. Individual workspaces/projects
        # ----------------------------------------------------

        individual_results = {}

        for email, (workspace_name, project_name) in (
            INDIVIDUAL_RESOURCES.items()
        ):

            user = users[email]

            workspace = get_or_create_workspace(
                db,
                user,
                workspace_name,
            )

            ensure_workspace_membership(
                db,
                workspace.id,
                user.id,
                WorkspaceRole.OWNER,
            )

            project = get_or_create_project(
                db,
                workspace,
                user,
                project_name,
            )

            ensure_project_membership(
                db,
                project.id,
                user.id,
                ProjectRole.OWNER,
            )

            individual_results[email] = {
                "workspace": workspace,
                "project": project,
            }

        # ----------------------------------------------------
        # 3. Shared Sprint 7 workspace
        # ----------------------------------------------------

        owner = users["akhil@example.com"]

        lab_workspace = get_or_create_workspace(
            db,
            owner,
            LAB_WORKSPACE_NAME,
        )

        # Add all seven users to lab workspace
        for email, role in LAB_WORKSPACE_ROLES.items():

            ensure_workspace_membership(
                db,
                lab_workspace.id,
                users[email].id,
                role,
            )

        # ----------------------------------------------------
        # 4. Shared Sprint 7 project
        # ----------------------------------------------------

        lab_project = get_or_create_project(
            db,
            lab_workspace,
            owner,
            LAB_PROJECT_NAME,
        )

        # Add first four users with project roles
        for email, role in LAB_PROJECT_ROLES.items():

            ensure_project_membership(
                db,
                lab_project.id,
                users[email].id,
                role,
            )

        # ----------------------------------------------------
        # 5. Commit everything
        # ----------------------------------------------------

        db.commit()

        # ----------------------------------------------------
        # 6. Generate tracking document
        # ----------------------------------------------------

        output = []

        output.append("# Milestone 2 Test Data\n")
        output.append(
            f"Generated: {datetime.now().isoformat()}\n"
        )

        output.append("\n## Users\n")

        output.append(
            "| Email | User ID | Global Role |"
        )
        output.append(
            "|---|---|---|"
        )

        for email, user in users.items():

            output.append(
                f"| `{email}` | `{user.id}` | `{user.role}` |"
            )

        output.append(
            "\n> Global role is separate from workspace/project roles."
        )

        output.append(
            "\n## Individual Workspaces and Projects\n"
        )

        output.append(
            "| User | Workspace | Workspace ID | Project | Project ID |"
        )
        output.append(
            "|---|---|---|---|---|"
        )

        for email, resources in individual_results.items():

            workspace = resources["workspace"]
            project = resources["project"]

            output.append(
                f"| `{email}` "
                f"| `{workspace.name}` "
                f"| `{workspace.id}` "
                f"| `{project.title}` "
                f"| `{project.id}` |"
            )

        output.append(
            "\n## Shared Sprint 7 Lab\n"
        )

        output.append(
            f"Workspace: `{lab_workspace.name}`"
        )

        output.append(
            f"\nWorkspace ID: `{lab_workspace.id}`"
        )

        output.append(
            f"\nProject: `{lab_project.title}`"
        )

        output.append(
            f"\nProject ID: `{lab_project.id}`\n"
        )

        output.append(
            "\n### Workspace Memberships\n"
        )

        output.append(
            "| User | Workspace Role |"
        )

        output.append(
            "|---|---|"
        )

        for email, role in LAB_WORKSPACE_ROLES.items():

            output.append(
                f"| `{email}` | `{role.value}` |"
            )

        output.append(
            "\n### Project Memberships\n"
        )

        output.append(
            "| User | Project Role |"
        )

        output.append(
            "|---|---|"
        )

        for email, role in LAB_PROJECT_ROLES.items():

            output.append(
                f"| `{email}` | `{role.value}` |"
            )

        output.append(
            "\n> session_test, rotation_test and "
            "logout_test are intentionally workspace members "
            "but NOT project members of the Sprint 7 lab."
        )

        map_path = (
            Path(__file__).parent
            / "MILESTONE2_TEST_DATA.md"
        )

        map_path.write_text(
            "\n".join(output),
            encoding="utf-8",
        )

        # ----------------------------------------------------
        # 7. Terminal summary
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("MILESTONE 2 TEST DATA CREATED")
        print("=" * 70)

        print("\nINDIVIDUAL RESOURCES\n")

        for email, resources in individual_results.items():

            workspace = resources["workspace"]
            project = resources["project"]

            print(f"USER:      {email}")
            print(f"WORKSPACE: {workspace.name}")
            print(f"WS ID:     {workspace.id}")
            print(f"PROJECT:   {project.title}")
            print(f"PROJECT ID:{project.id}")
            print("-" * 70)

        print("\nSHARED SPRINT 7 LAB\n")

        print(
            f"WORKSPACE: {lab_workspace.name}"
        )

        print(
            f"WS ID:     {lab_workspace.id}"
        )

        print(
            f"PROJECT:   {lab_project.title}"
        )

        print(
            f"PROJECT ID:{lab_project.id}"
        )

        print(
            "\nTracking file created:"
        )

        print(
            map_path
        )

        print(
            "\nSEED COMPLETE."
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()