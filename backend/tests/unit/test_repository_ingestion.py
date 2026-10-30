import hashlib
from pathlib import Path

import pytest

from app.utils.repository_ingestion import (
    RepositoryFileScanner,
    RepositoryValidationError,
    detect_language,
    validate_github_url,
)


@pytest.mark.parametrize("url, expected", [
    ("https://github.com/acme/widget", ("https://github.com/acme/widget", "acme", "widget")),
    ("https://github.com/acme/widget.git", ("https://github.com/acme/widget", "acme", "widget")),
    ("https://github.com/acme/widget/", ("https://github.com/acme/widget", "acme", "widget")),
])
def test_validate_github_urls(url, expected):
    assert validate_github_url(url) == expected


@pytest.mark.parametrize("url", [
    "http://github.com/acme/widget",
    "git@github.com:acme/widget.git",
    "https://evil.com/acme/widget",
    "https://user:pass@github.com/acme/widget",
    "https://github.com/acme/widget?x=1",
    "https://github.com/acme/widget#readme",
    "https://github.com:443/acme/widget",
    "https://github.com/acme/widget:443/repo",
])
def test_reject_invalid_github_urls(url):
    with pytest.raises(RepositoryValidationError):
        validate_github_url(url)


def test_scanner_filters_and_hashes(tmp_path):
    (tmp_path / "src").mkdir()
    source = tmp_path / "src" / "main.py"
    source.write_text("print('hello')", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
    (tmp_path / ".env.local").write_text("SECRET=1", encoding="utf-8")
    (tmp_path / ".env.example").write_text("SECRET=example", encoding="utf-8")
    (tmp_path / "binary.bin").write_bytes(b"abc\x00def")

    files = RepositoryFileScanner().scan(str(tmp_path))
    paths = {item.path for item in files}
    assert "src/main.py" in paths
    assert ".env.local" not in paths
    assert ".env.example" in paths
    assert "node_modules/ignored.js" not in paths
    assert "binary.bin" not in paths
    main = next(item for item in files if item.path == "src/main.py")
    assert main.language == "python"
    assert main.content_hash == hashlib.sha256(b"print('hello')").hexdigest()


def test_language_detection_and_symlink(tmp_path):
    assert detect_language("src/App.tsx") == "tsx"
    assert detect_language("README.unknown") == "unknown"
    external = tmp_path.parent / "outside-repository.txt"
    external.write_text("outside", encoding="utf-8")
    try:
        (tmp_path / "linked.txt").symlink_to(external)
        files = RepositoryFileScanner().scan(str(tmp_path))
        assert files == []
    except OSError:
        pytest.skip("Symlink creation is not permitted in this environment")
    finally:
        if external.exists(): external.unlink()
