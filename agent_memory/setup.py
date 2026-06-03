from __future__ import annotations

import json
from pathlib import Path

import yaml


MEMORY_FILES = {
    "profile.md": "# Profile\n\n",
    "projects.md": "# Projects\n\n",
    "lessons.md": "# Lessons\n\n",
    "workflows.md": "# Workflows\n\n",
    "infra.md": "# Infrastructure\n\n",
    "bootstrap.md": "# Bootstrap\n\n",
}


def setup_workspace(
    root: Path,
    *,
    workspace: str,
    machines: list[str],
    adapters: list[str],
    force: bool = False,
) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    config_file = root / "agentmemory.yaml"
    if config_file.exists() and not force:
        return {"status": "exists", "path": str(config_file)}

    payload = {
        "version": 1,
        "workspace": {
            "name": workspace,
            "mode": "git-backed",
        },
        "machines": [{"id": machine, "label": machine} for machine in machines],
        "trigger_aliases": {
            "shared": ["保存到共享记忆", "同步给其他 agent", "save to shared memory"],
            "refresh": ["拉取一下云端的记忆", "刷新共享记忆", "refresh shared memory"],
            "local": ["记住这个", "保存到记忆", "remember this"],
        },
        "memory": {
            "canonical_dir": "memory",
            "inbox_dir": "inbox",
            "archive_dir": "archive",
        },
        "curator": {
            "require_manual_apply": True,
            "secret_scan": "strict",
            "auto_merge": False,
        },
        "cloud": {
            "backend": "git",
            "remote": "origin",
            "branch": "main",
        },
        "adapters": {
            adapter: {"adapter": f"adapters/{adapter}.yaml"} for adapter in adapters
        },
    }
    config_file.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")

    memory_dir = root / "memory"
    memory_dir.mkdir(exist_ok=True)
    for filename, content in MEMORY_FILES.items():
        path = memory_dir / filename
        if force or not path.exists():
            path.write_text(content, encoding="utf-8")

    registry_dir = root / "registry"
    registry_dir.mkdir(exist_ok=True)
    (registry_dir / "agents.json").write_text(
        json.dumps({"version": 1, "agents": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (registry_dir / "invitations.json").write_text(
        json.dumps({"version": 1, "invited_machine_agent_pairs": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    for machine in machines:
        for adapter in adapters:
            (root / "inbox" / machine / adapter).mkdir(parents=True, exist_ok=True)

    curator_dir = root / ".curator"
    curator_dir.mkdir(exist_ok=True)
    (curator_dir / "manifest.json").write_text(
        json.dumps({"version": 0}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (curator_dir / "processed.jsonl").write_text("", encoding="utf-8")

    return {"status": "created", "path": str(config_file)}

