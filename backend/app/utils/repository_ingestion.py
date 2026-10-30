import os
import re
import shutil
import subprocess
import tempfile
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


class RepositoryValidationError(ValueError): pass
class RepositoryCloneError(RuntimeError): pass
class RepositoryLimitError(RuntimeError): pass

@dataclass(frozen=True)
class GitSnapshot:
    clone_path: str
    commit_sha: str | None
    branch: str | None


def validate_github_url(url: str) -> tuple[str, str, str]:
    if not isinstance(url, str) or url != url.strip() or not url:
        raise RepositoryValidationError("Repository URL is invalid")
    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise RepositoryValidationError("Repository URL is invalid") from exc
    if parsed.scheme != "https": raise RepositoryValidationError("Repository URL must use HTTPS")
    if parsed.username or parsed.password: raise RepositoryValidationError("Repository URL must not contain credentials")
    if parsed.hostname != "github.com": raise RepositoryValidationError("Only github.com repositories are supported")
    try:
        port = parsed.port
    except ValueError as exc:
        raise RepositoryValidationError("Repository URL is invalid") from exc
    if port is not None: raise RepositoryValidationError("Repository URL must not contain a port")
    if parsed.query or parsed.fragment: raise RepositoryValidationError("Repository URL must not contain a query or fragment")

    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2: raise RepositoryValidationError("Repository URL must contain an owner and repository name")
    owner, repository = parts
    if repository.endswith(".git"): repository = repository[:-4]
    if not owner or not repository: raise RepositoryValidationError("Repository URL is invalid")
    if owner in (".", "..") or repository in (".", ".."): raise RepositoryValidationError("Repository URL is invalid")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?", owner): raise RepositoryValidationError("Repository owner is invalid")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", repository): raise RepositoryValidationError("Repository name is invalid")
    return f"https://github.com/{owner}/{repository}", owner, repository

normalize_github_repository_url = validate_github_url


class GitHubPublicRepositoryVerifier:
    def __init__(self, timeout_seconds: int = 15):
        self.timeout_seconds = timeout_seconds

    def verify(self, owner: str, name: str) -> None:
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise urllib.error.HTTPError(newurl, code, "Redirects are not allowed", headers, fp)

        request = urllib.request.Request(
            f"https://api.github.com/repos/{owner}/{name}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "ai-workspace-ingestion"},
            method="GET",
        )
        opener = urllib.request.build_opener(NoRedirectHandler())
        try:
            with opener.open(request, timeout=self.timeout_seconds) as response:
                if response.status != 200:
                    raise RepositoryValidationError("GitHub repository is not publicly accessible")
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RepositoryValidationError("GitHub repository is not publicly accessible") from exc

        if payload.get("private") is True or payload.get("archived") is True or payload.get("visibility") not in {None, "public"}:
            raise RepositoryValidationError("Only public, active GitHub repositories are supported")


class GitHubCloneAdapter:
    def __init__(self, timeout_seconds: int = 120): self.timeout_seconds = timeout_seconds

    def clone(self, url: str, destination: str):
        env = os.environ.copy()
        for key in list(env):
            if key.upper().startswith("GIT_") or key.upper() in {"SSH_ASKPASS", "GIT_ASKPASS", "GCM_INTERACTIVE"}:
                env.pop(key, None)
        env.update({
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_ASKPASS": os.devnull,
            "SSH_ASKPASS": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        })
        try:
            completed = subprocess.run([
                "git", "-c", "http.followRedirects=false",
                "-c", "credential.helper=",
                "-c", "core.askPass=false",
                "clone", "--depth", "1", "--single-branch", "--no-tags", url, destination,
            ], capture_output=True, timeout=self.timeout_seconds, check=False, shell=False, env=env)
        except FileNotFoundError as exc:
            raise RepositoryCloneError("Git is not installed or is not available") from exc
        except subprocess.TimeoutExpired as exc:
            raise RepositoryCloneError("Repository clone timed out") from exc
        if completed.returncode != 0: raise RepositoryCloneError("Repository clone failed")
        commit_sha = self._git_output(destination, ["rev-parse", "HEAD"])
        branch = self._git_output(destination, ["branch", "--show-current"])
        return GitSnapshot(destination, commit_sha, branch)

    @staticmethod
    def _git_output(repo_path: str, args: list[str]) -> str | None:
        try:
            result = subprocess.run(["git", "-C", repo_path, *args], capture_output=True, text=True,
                                    timeout=10, check=False, shell=False)
            if result.returncode == 0:
                return result.stdout.strip() or None
        except (FileNotFoundError, subprocess.TimeoutExpired): return None
        return None


EXCLUDED_DIRECTORIES = {".git", "node_modules", "venv", ".venv", "env", "dist", "build", "__pycache__", ".next", "coverage"}
LANGUAGE_BY_EXTENSION = {
    ".py":"python", ".java":"java", ".js":"javascript", ".jsx":"jsx", ".ts":"typescript", ".tsx":"tsx",
    ".go":"go", ".rs":"rust", ".c":"c", ".h":"c", ".cc":"cpp", ".cpp":"cpp", ".cxx":"cpp", ".hpp":"cpp",
    ".cs":"csharp", ".kt":"kotlin", ".kts":"kotlin", ".swift":"swift", ".rb":"ruby", ".php":"php",
    ".html":"html", ".htm":"html", ".css":"css", ".scss":"scss", ".sass":"scss", ".sql":"sql",
    ".sh":"shell", ".bash":"shell", ".zsh":"shell", ".yaml":"yaml", ".yml":"yaml", ".json":"json",
    ".md":"markdown", ".markdown":"markdown", ".xml":"xml",
}

def detect_language(relative_path: str) -> str:
    return LANGUAGE_BY_EXTENSION.get(Path(relative_path).suffix.lower(), "unknown")

@dataclass(frozen=True)
class FileMetadata:
    path: str
    language: str
    size_bytes: int
    content_hash: str


class RepositoryFileScanner:
    def __init__(self, max_file_bytes: int = 1_000_000, max_files: int = 20_000,
                 max_total_bytes: int = 100_000_000, max_processing_seconds: int = 120,
                 excluded_directories: set[str] | None = None):
        self.max_file_bytes = max_file_bytes
        self.max_files = max_files
        self.max_total_bytes = max_total_bytes
        self.max_processing_seconds = max_processing_seconds
        self.excluded_directories = excluded_directories or EXCLUDED_DIRECTORIES

    @staticmethod
    def is_excluded_file(relative_path: str) -> bool:
        name = Path(relative_path).name.lower()
        lower = relative_path.lower().replace("\\", "/")
        safe_examples = {".env.example", ".env.sample", ".env.template", "env.example", "env.sample"}
        if name in safe_examples:
            return False
        if name in {".env", ".npmrc", "production.env", "credentials.json", "secrets.json", "id_rsa", "id_dsa", "id_ed25519", "id_ecdsa", "private.key", "server.key"}:
            return True
        if name.startswith(".env.") or name.endswith(".env"):
            return True
        if lower == ".aws/credentials" or lower.startswith(".aws/") and name in {"credentials", "config"}:
            return True
        if name.endswith((".tfstate", ".tfstate.backup")):
            return True
        if "service-account" in name and name.endswith(".json"):
            return True
        if name.endswith((".pem", ".key", ".p12", ".pfx", ".crt", ".keystore", ".jks")):
            return True
        return lower.endswith("/credentials") or lower.endswith("/secrets") or "/.github/credentials" in lower

    def scan(self, root: str) -> list[FileMetadata]:
        import hashlib, time
        root_path = Path(root).resolve()
        start = time.monotonic()
        files: list[FileMetadata] = []
        total_bytes = 0
        for current_root, dirnames, filenames in os.walk(root_path, followlinks=False):
            current = Path(current_root)
            dirnames[:] = sorted(name for name in dirnames if name not in self.excluded_directories and not (current / name).is_symlink())
            for filename in sorted(filenames):
                if time.monotonic() - start > self.max_processing_seconds: raise RepositoryLimitError("Repository processing time limit exceeded")
                path = current / filename
                if path.is_symlink(): continue
                try:
                    resolved = path.resolve(strict=True)
                    resolved.relative_to(root_path)
                except (FileNotFoundError, RuntimeError, ValueError, OSError): continue
                relative = resolved.relative_to(root_path).as_posix()
                if self.is_excluded_file(relative): continue
                try: stat = path.stat()
                except OSError: continue
                if stat.st_size == 0 or stat.st_size > self.max_file_bytes: continue
                if len(files) >= self.max_files: raise RepositoryLimitError("Repository file count limit exceeded")
                try: data = path.read_bytes()
                except OSError: continue
                if b"\x00" in data: continue
                try: data.decode("utf-8")
                except UnicodeDecodeError: continue
                if total_bytes + len(data) > self.max_total_bytes: raise RepositoryLimitError("Repository processed-byte limit exceeded")
                total_bytes += len(data)
                files.append(FileMetadata(relative, detect_language(relative), len(data), hashlib.sha256(data).hexdigest()))
        return files


def create_temporary_clone_directory() -> str:
    return tempfile.mkdtemp(prefix="ai-workspace-repo-")


def cleanup_temporary_directory(path: str | None) -> None:
    if path: shutil.rmtree(path, ignore_errors=True)
