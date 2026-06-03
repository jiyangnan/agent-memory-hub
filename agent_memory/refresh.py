from __future__ import annotations

from pathlib import Path

from .cloud import cloud_pull
from .sync import sync_apply, sync_dry_run


def refresh_shared_memory(
    root: Path,
    *,
    home: Path,
    machine: str,
    agent: str,
    apply: bool = False,
    remote: str = "origin",
    branch: str | None = None,
) -> dict:
    pull = cloud_pull(root, remote=remote, branch=branch)
    if pull["status"] != "up_to_date":
        return {
            "status": "pull_blocked",
            "pull": pull,
            "sync": {"status": "not_started"},
        }

    if apply:
        sync = sync_apply(root, home=home, machine=machine, agent=agent)
        status = "sync_applied" if sync["status"] in ("applied", "no_change") else "sync_blocked"
    else:
        sync = sync_dry_run(root, home=home, machine=machine, agent=agent)
        status = "sync_ready" if sync["status"] in ("would_update", "no_change") else "sync_blocked"

    return {
        "status": status,
        "pull": pull,
        "sync": sync,
    }
