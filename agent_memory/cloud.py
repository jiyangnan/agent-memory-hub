from __future__ import annotations

import subprocess
from pathlib import Path


SHARED_STATE_PATHS = (
    "agentmemory.yaml",
    "memory",
    "inbox",
    "archive",
    "registry",
    ".curator/manifest.json",
    ".curator/processed.jsonl",
)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def is_git_repository(root: Path) -> bool:
    result = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def current_branch(root: Path) -> str:
    result = run_git(root, ["symbolic-ref", "--short", "HEAD"])
    if result.returncode == 0:
        return result.stdout.strip()
    return "HEAD"


def remote_exists(root: Path, remote: str) -> bool:
    return run_git(root, ["remote", "get-url", remote]).returncode == 0


def porcelain_status(root: Path) -> list[str]:
    result = run_git(root, ["status", "--porcelain"])
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def staged_paths(root: Path) -> list[str]:
    result = run_git(root, ["diff", "--cached", "--name-only"])
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_shared_state_path(path: str) -> bool:
    normalized = path.strip().lstrip("./")
    return any(normalized == allowed or normalized.startswith(f"{allowed}/") for allowed in SHARED_STATE_PATHS)


def cloud_status(root: Path, *, remote: str = "origin") -> dict:
    branch = current_branch(root)
    if not is_git_repository(root):
        return {"status": "not_git", "remote": remote, "branch": branch, "paths": []}
    if not remote_exists(root, remote):
        return {"status": "missing_remote", "remote": remote, "branch": branch, "paths": []}
    paths = porcelain_status(root)
    if paths:
        return {"status": "dirty", "remote": remote, "branch": branch, "paths": paths}
    return {"status": "ready", "remote": remote, "branch": branch, "paths": []}


def cloud_save(root: Path, *, message: str, remote: str = "origin") -> dict:
    branch = current_branch(root)
    if not is_git_repository(root):
        return {"status": "not_git", "remote": remote, "branch": branch, "paths": []}
    existing = [path for path in SHARED_STATE_PATHS if (root / path).exists()]
    add = run_git(root, ["add", "--", *existing])
    if add.returncode != 0:
        return {"status": "git_add_failed", "remote": remote, "branch": branch, "paths": [], "stderr": add.stderr}
    paths = staged_paths(root)
    if not paths:
        return {"status": "no_change", "remote": remote, "branch": branch, "paths": []}
    non_shared = [path for path in paths if not is_shared_state_path(path)]
    if non_shared:
        return {"status": "staged_non_shared_state", "remote": remote, "branch": branch, "paths": non_shared}
    commit = run_git(root, ["commit", "-m", message])
    if commit.returncode != 0:
        return {"status": "commit_failed", "remote": remote, "branch": branch, "paths": paths, "stderr": commit.stderr}
    return {"status": "committed", "remote": remote, "branch": branch, "paths": paths}


def remote_branch_exists(root: Path, *, remote: str, branch: str) -> bool:
    result = run_git(root, ["ls-remote", "--heads", remote, branch])
    return result.returncode == 0 and bool(result.stdout.strip())


def cloud_pull(root: Path, *, remote: str = "origin", branch: str | None = None) -> dict:
    active_branch = branch or current_branch(root)
    if not is_git_repository(root):
        return {"status": "not_git", "remote": remote, "branch": active_branch, "paths": []}
    if not remote_exists(root, remote):
        return {"status": "missing_remote", "remote": remote, "branch": active_branch, "paths": []}
    dirty = porcelain_status(root)
    if dirty:
        return {"status": "dirty", "remote": remote, "branch": active_branch, "paths": dirty}
    if not remote_branch_exists(root, remote=remote, branch=active_branch):
        return {"status": "up_to_date", "remote": remote, "branch": active_branch, "paths": []}
    pull = run_git(root, ["pull", "--ff-only", remote, active_branch])
    if pull.returncode != 0:
        return {"status": "pull_failed", "remote": remote, "branch": active_branch, "paths": [], "stderr": pull.stderr}
    return {"status": "up_to_date", "remote": remote, "branch": active_branch, "paths": []}


def cloud_push(root: Path, *, remote: str = "origin", branch: str | None = None) -> dict:
    active_branch = branch or current_branch(root)
    if not is_git_repository(root):
        return {"status": "not_git", "remote": remote, "branch": active_branch, "paths": []}
    if not remote_exists(root, remote):
        return {"status": "missing_remote", "remote": remote, "branch": active_branch, "paths": []}
    dirty = porcelain_status(root)
    if dirty:
        return {"status": "dirty", "remote": remote, "branch": active_branch, "paths": dirty}
    push = run_git(root, ["push", remote, active_branch])
    if push.returncode != 0:
        return {"status": "push_failed", "remote": remote, "branch": active_branch, "paths": [], "stderr": push.stderr}
    return {"status": "pushed", "remote": remote, "branch": active_branch, "paths": []}

