from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project

print("User relationships:")
print(User.projects.property.back_populates)

print("Workspace relationships:")
print(Workspace.projects.property.back_populates)

print("Project relationships:")
print(Project.creator.property.back_populates)
print(Project.workspace.property.back_populates)