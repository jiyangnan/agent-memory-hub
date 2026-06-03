from __future__ import annotations

import json
import shutil
from datetime import date, datetime
from pathlib import Path

from .config import load_config
from .safety import contains_secret


DESTINATIONS = {
    "preference": "memory/profile.md",
    "project": "memory/projects.md",
    "lesson": "memory/lessons.md",
    "workflow": "memory/workflows.md",
    "infra": "memory/infra.md",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata


def pending_notes(root: Path) -> list[Path]:
    config = load_config(root)
    inbox_dir = root / config.get("memory", {}).get("inbox_dir", "inbox")
    if not inbox_dir.exists():
        return []
    return sorted(inbox_dir.glob("**/*.md"))


def scan_status(root: Path) -> dict:
    pending = 0
    invalid = 0
    secret_blocked = 0
    notes: list[str] = []
    for path in pending_notes(root):
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        pending += 1
        notes.append(str(path.relative_to(root)))
        if not metadata.get("id") or not metadata.get("type"):
            invalid += 1
        if contains_secret(text):
            secret_blocked += 1
    return {
        "pending_notes": pending,
        "invalid_notes": invalid,
        "secret_blocked_notes": secret_blocked,
        "notes": notes,
    }


def section_text(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    next_heading = text.find("\n## ", start + 1)
    body = text[start: next_heading if next_heading != -1 else len(text)]
    return body.strip()


def archive_note(root: Path, path: Path, status: str) -> Path:
    today = date.today()
    archive_dir = root / "archive" / status / f"{today.year:04d}" / f"{today.month:02d}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    destination = archive_dir / path.name
    shutil.move(str(path), destination)
    return destination


def append_processed(root: Path, *, note_id: str, status: str, archive_path: Path, fact: str) -> None:
    processed = root / ".curator" / "processed.jsonl"
    processed.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": note_id,
        "status": status,
        "archive_path": str(archive_path.relative_to(root)),
        "fact": fact,
        "processed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with processed.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def update_manifest(root: Path) -> int:
    manifest_path = root / ".curator" / "manifest.json"
    if manifest_path.exists():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = {}
    version = int(payload.get("version", 0)) + 1
    payload.update(
        {
            "version": version,
            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return version


def append_canonical(root: Path, destination: str, text: str, metadata: dict[str, str]) -> None:
    target = root / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    fact = section_text(text, "Fact")
    why = section_text(text, "Why It Matters")
    evidence = section_text(text, "Evidence")
    block = (
        f"\n## {metadata.get('id', 'note')}\n\n"
        f"- Fact: {fact}\n"
        f"- Why: {why}\n"
        f"- Evidence: {evidence}\n"
    )
    with target.open("a", encoding="utf-8") as handle:
        handle.write(block)


def curate_apply(root: Path, *, machine: str, agent: str) -> dict:
    accepted = 0
    needs_review = 0
    processed: list[str] = []
    for path in pending_notes(root):
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        note_id = metadata.get("id", path.stem)
        fact = section_text(text, "Fact")
        if contains_secret(text) or not metadata.get("type"):
            archive_path = archive_note(root, path, "needs_user_review")
            append_processed(root, note_id=note_id, status="needs_user_review", archive_path=archive_path, fact=fact)
            needs_review += 1
            processed.append(note_id)
            continue
        destination = DESTINATIONS.get(metadata["type"])
        if not destination:
            archive_path = archive_note(root, path, "needs_user_review")
            append_processed(root, note_id=note_id, status="needs_user_review", archive_path=archive_path, fact=fact)
            needs_review += 1
            processed.append(note_id)
            continue
        append_canonical(root, destination, text, metadata)
        archive_path = archive_note(root, path, "accepted")
        append_processed(root, note_id=note_id, status="accepted", archive_path=archive_path, fact=fact)
        accepted += 1
        processed.append(note_id)
    version = update_manifest(root) if accepted or needs_review else json.loads((root / ".curator" / "manifest.json").read_text(encoding="utf-8")).get("version", 0)
    return {
        "accepted": accepted,
        "needs_review": needs_review,
        "processed": processed,
        "manifest_version": version,
        "machine": machine,
        "agent": agent,
    }

