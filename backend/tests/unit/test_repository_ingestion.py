import hashlib
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.utils.repository_ingestion import (
    GitHubCloneAdapter,
    GitHubPublicRepositoryVerifier,
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


def test_sensitive_files_and_safe_examples_are_filtered(tmp_path):
    sensitive = [
        ".aws/credentials",
        ".npmrc",
        "production.env",
        "config.production.env",
        "terraform.tfstate",
        "terraform.tfstate.backup",
        "service-account-prod.json",
        "credentials.json",
        "private.key",
        "id_rsa",
    ]
    for relative in sensitive:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("secret", encoding="utf-8")
    for safe in [".env.example", ".env.sample"]:
        (tmp_path / safe).write_text("SECRET=example", encoding="utf-8")

    files = RepositoryFileScanner().scan(str(tmp_path))
    paths = {item.path for item in files}
    assert not (set(sensitive) & paths)
    assert ".env.example" in paths
    assert ".env.sample" in paths


def test_clone_disables_credentials_helpers_prompting_and_git_config(monkeypatch, tmp_path):
    import app.utils.repository_ingestion as repository_ingestion

    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        if "clone" in args:
            return SimpleNamespace(returncode=0, stdout="")
        if "rev-parse" in args:
            return SimpleNamespace(returncode=0, stdout="a" * 40 + "\n")
        return SimpleNamespace(returncode=0, stdout="main\n")

    monkeypatch.setattr(repository_ingestion.subprocess, "run", fake_run)
    snapshot = GitHubCloneAdapter(timeout_seconds=5).clone(
        "https://github.com/acme/public", str(tmp_path / "checkout")
    )

    clone_args, clone_kwargs = calls[0]
    env = clone_kwargs["env"]
    assert "-c" in clone_args and "credential.helper=" in clone_args
    assert "http.followRedirects=false" in clone_args
    assert env["GIT_TERMINAL_PROMPT"] == "0"
    assert env["GCM_INTERACTIVE"] == "Never"
    assert env["GIT_CONFIG_NOSYSTEM"] == "1"
    assert env["GIT_CONFIG_GLOBAL"] == os.devnull
    assert "GIT_CONFIG_COUNT" not in env
    assert snapshot.commit_sha == "a" * 40


def test_public_verifier_rejects_private_repository(monkeypatch):
    import app.utils.repository_ingestion as repository_ingestion

    class FakeResponse:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"private": true, "visibility": "private"}'

    class FakeOpener:
        def open(self, request, timeout): return FakeResponse()

    monkeypatch.setattr(repository_ingestion.urllib.request, "build_opener", lambda *args: FakeOpener())
    with pytest.raises(RepositoryValidationError, match="Only public"):
        GitHubPublicRepositoryVerifier(timeout_seconds=1).verify("acme", "private")


def test_public_verifier_accepts_public_repository(monkeypatch):
    import app.utils.repository_ingestion as repository_ingestion

    class FakeResponse:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"private": false, "visibility": "public"}'

    class FakeOpener:
        def open(self, request, timeout): return FakeResponse()

    monkeypatch.setattr(repository_ingestion.urllib.request, "build_opener", lambda *args: FakeOpener())
    GitHubPublicRepositoryVerifier(timeout_seconds=1).verify("acme", "public")
