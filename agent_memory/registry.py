from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def registry_file(root: Path) -> Path:
    return root / "registry" / "agents.json"


def load_registry(root: Path) -> dict:
    path = registry_file(root)
    if not path.exists():
        return {"version": 1, "agents": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(root: Path, payload: dict) -> None:
    path = registry_file(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def register_agent(
    root: Path,
    *,
    machine: str,
    agent: str,
    primary_memory: str,
    adapter: str = "",
    skill_target: str = "",
) -> dict:
    payload = load_registry(root)
    agents = payload.setdefault("agents", [])
    existing = next((item for item in agents if item["machine"] == machine and item["agent"] == agent), None)
    record = {
        "machine": machine,
        "agent": agent,
        "adapter": adapter or agent,
        "primary_memory": primary_memory,
        "skill_target": skill_target,
        "registered_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if existing:
        existing.update(record)
        record = existing
    else:
        agents.append(record)
    save_registry(root, payload)
    (root / "inbox" / machine / agent).mkdir(parents=True, exist_ok=True)
    return record


def find_agent(root: Path, *, machine: str, agent: str) -> dict | None:
    payload = load_registry(root)
    return next((item for item in payload.get("agents", []) if item["machine"] == machine and item["agent"] == agent), None)


def render_members(root: Path) -> str:
    payload = load_registry(root)
    lines = ["# agent memory hub members", ""]
    if not payload.get("agents"):
        lines.append("No registered agents.")
    for item in payload.get("agents", []):
        lines.append(f"- {item['machine']}/{item['agent']} -> {item['primary_memory']}")
    return "\n".join(lines) + "\n"

