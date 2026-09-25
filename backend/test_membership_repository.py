import sys
from pathlib import Path


# Ensure the backend directory is available when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.repositories.workspace_member_repository import WorkspaceMemberRepository

print("Repository Loaded Successfully")