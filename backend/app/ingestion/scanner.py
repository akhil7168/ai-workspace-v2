from dataclasses import dataclass
from pathlib import Path

from app.utils.repository_ingestion import FileMetadata, RepositoryFileScanner


@dataclass(frozen=True)
class SourceFile:
    relative_path: str
    language: str
    content: str
    size_bytes: int


class IngestionSourceScanner:
    """Reads only files already approved and accounted for by the Day 9 scan."""

    def read_files(self, clone_root: str, metadata: list[FileMetadata],
                  max_file_bytes: int = 1_000_000) -> list[SourceFile]:
        root = Path(clone_root).resolve()
        source_files: list[SourceFile] = []
        for item in metadata:
            candidate = (root / item.path).resolve(strict=False)
            try:
                candidate.relative_to(root)
            except ValueError:
                continue
            if candidate.is_symlink() or not candidate.is_file():
                continue
            relative = candidate.relative_to(root).as_posix()
            if RepositoryFileScanner.is_excluded_file(relative):
                continue
            try:
                size = candidate.stat().st_size
            except OSError:
                continue
            if size <= 0 or size > max_file_bytes:
                continue
            try:
                content_bytes = candidate.read_bytes()
                content = content_bytes.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            source_files.append(SourceFile(relative, item.language, content, len(content_bytes)))
        return source_files
