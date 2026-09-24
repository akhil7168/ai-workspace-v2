from app.models.workspace_member import WorkspaceMember
from app.models.workspace import Workspace
from app.models.user import User

print("WorkspaceMember Table :", WorkspaceMember.__tablename__)
print("Workspace Relationship :", WorkspaceMember.workspace.property.back_populates)
print("User Relationship :", WorkspaceMember.user.property.back_populates)
print("Primary Keys :", WorkspaceMember.__table__.primary_key.columns.keys())