from pathlib import Path


def test_ai_architecture_document_has_required_sections_and_diagrams():
    document_path = Path(__file__).resolve().parents[3] / "docs" / "ai-architecture.md"
    document = document_path.read_text(encoding="utf-8")

    required_sections = (
        "# AI Workspace",
        "## Product definition",
        "## Current state and target state",
        "## Current backend architecture and reuse points",
        "## Target architecture",
        "### Component architecture",
        "### Ingestion and question flows",
        "### Logical data model",
        "## Repository ingestion design",
        "## Security and multi-tenancy",
        "## API evolution",
        "## Implementation roadmap",
        "## Days 5–7 alignment and verified gaps",
        "## Decisions, unresolved choices, and risks",
    )
    assert all(section in document for section in required_sections)
    assert document.count("```mermaid") == 3
    assert "not implemented" in document
    assert "planned, not available" in document
