from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

print("User memberships ->", User.workspace_memberships.property.back_populates)
print("Workspace members ->", Workspace.members.property.back_populates)
print("WorkspaceMember.user ->", WorkspaceMember.user.property.back_populates)
print("WorkspaceMember.workspace ->", WorkspaceMember.workspace.property.back_populates)

print("\nSprint 3 Step 3.3 Relationships OK")