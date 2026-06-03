from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import yaml

from .registry import find_agent


BEGIN = "<!-- agent-memory-hub:BEGIN shared -->"
END = "<!-- agent-memory-hub:END shared -->"


def load_adapter(root: Path, adapter_id: str) -> dict:
    path = root / "adapters" / f"{adapter_id}.yaml"
    if not path.exists():
        path = Path(__file__).resolve().parents[1] / "adapters" / f"{adapter_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"missing adapter manifest: {adapter_id}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def expand_home(home: Path, value: str) -> Path:
    if value.startswith("~/"):
        return home / value[2:]
    return Path(value)


def target_for_agent(root: Path, home: Path, *, machine: str, agent: str) -> tuple[Path, Path]:
    record = find_agent(root, machine=machine, agent=agent)
    if not record:
        raise ValueError(f"agent is not registered: {machine}/{agent}")
    adapter = load_adapter(root, record.get("adapter") or agent)
    target = expand_home(home, record.get("primary_memory") or adapter["primary_memory"]["path"])
    allowlist = adapter.get("allowlist") or [str(target.parent)]
    allowed_root = expand_home(home, allowlist[0])
    return target, allowed_root


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def render_shared_memory(root: Path) -> str:
    sections = []
    for name in ("profile", "projects", "lessons", "workflows", "infra", "bootstrap"):
        path = root / "memory" / f"{name}.md"
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                sections.append(f"## {name}\n\n{content}")
    return "\n\n".join(sections).strip() + "\n"


def marker_block(content: str) -> str:
    return f"{BEGIN}\n{content.rstrip()}\n{END}"


def replace_managed_section(existing: str, content: str) -> tuple[str, bool]:
    start = existing.find(BEGIN)
    end = existing.find(END)
    if start == -1 or end == -1 or end < start:
        return existing, False
    end += len(END)
    return existing[:start] + marker_block(content) + existing[end:], True


def backup_file(root: Path, target: Path, *, machine: str, agent: str) -> Path:
    backup_dir = root / ".curator" / "backups" / machine / agent
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds").replace(":", "-")
    backup = backup_dir / f"{timestamp}-{target.name}.bak"
    shutil.copy2(target, backup)
    return backup


def unsafe_result(target: Path, allowed_root: Path) -> dict:
    return {
        "status": "unsafe_target",
        "target_path": str(target),
        "message": f"target resolves outside allowlist: {allowed_root}",
    }


def sync_dry_run(root: Path, *, home: Path, machine: str, agent: str) -> dict:
    target, allowed_root = target_for_agent(root, home, machine=machine, agent=agent)
    if target.exists() and not is_within(target, allowed_root):
        return unsafe_result(target, allowed_root)
    if not target.exists():
        return {"status": "missing_target", "target_path": str(target), "preview": ""}
    existing = target.read_text(encoding="utf-8")
    updated, found = replace_managed_section(existing, render_shared_memory(root))
    if not found:
        return {"status": "missing_marker", "target_path": str(target), "preview": ""}
    return {"status": "would_update" if updated != existing else "no_change", "target_path": str(target), "preview": updated}


def install_marker(root: Path, *, home: Path, machine: str, agent: str) -> dict:
    target, allowed_root = target_for_agent(root, home, machine=machine, agent=agent)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not is_within(target, allowed_root):
        return unsafe_result(target, allowed_root)
    if not target.exists():
        target.write_text("", encoding="utf-8")
    existing = target.read_text(encoding="utf-8")
    if BEGIN in existing and END in existing:
        return {"status": "already_installed", "target_path": str(target), "backup_path": ""}
    backup = backup_file(root, target, machine=machine, agent=agent)
    target.write_text(existing.rstrip() + "\n\n" + marker_block("") + "\n", encoding="utf-8")
    return {"status": "installed", "target_path": str(target), "backup_path": str(backup)}


def write_local_sync_state(root: Path, *, machine: str, agent: str) -> None:
    manifest = root / ".curator" / "manifest.json"
    version = 0
    if manifest.exists():
        try:
            version = int(json.loads(manifest.read_text(encoding="utf-8")).get("version", 0))
        except (ValueError, json.JSONDecodeError):
            version = 0
    state_dir = root / ".curator" / "local-sync"
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "machine": machine,
        "agent": agent,
        "last_applied_version": version,
        "last_sync_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    (state_dir / f"{machine}-{agent}.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def sync_apply(root: Path, *, home: Path, machine: str, agent: str) -> dict:
    target, allowed_root = target_for_agent(root, home, machine=machine, agent=agent)
    if target.exists() and not is_within(target, allowed_root):
        return unsafe_result(target, allowed_root)
    if not target.exists():
        return {"status": "missing_target", "target_path": str(target), "backup_path": ""}
    existing = target.read_text(encoding="utf-8")
    updated, found = replace_managed_section(existing, render_shared_memory(root))
    if not found:
        return {"status": "missing_marker", "target_path": str(target), "backup_path": ""}
    if updated == existing:
        write_local_sync_state(root, machine=machine, agent=agent)
        return {"status": "no_change", "target_path": str(target), "backup_path": ""}
    backup = backup_file(root, target, machine=machine, agent=agent)
    target.write_text(updated, encoding="utf-8")
    write_local_sync_state(root, machine=machine, agent=agent)
    return {"status": "applied", "target_path": str(target), "backup_path": str(backup)}

