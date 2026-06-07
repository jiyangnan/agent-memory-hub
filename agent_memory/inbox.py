from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

from .config import load_config
from .safety import contains_secret, has_ambiguous_agent_family_wording


def normalized_hash(text: str) -> str:
    normalized = " ".join(text.strip().split())
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def safe_slug(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    return "-".join(part for part in slug.split("-") if part)[:80] or "note"


def add_inbox_note(
    root: Path,
    *,
    machine: str,
    agent: str,
    note_type: str,
    scope: str,
    fact: str,
    why: str,
    evidence: str,
    suggested_destination: str,
    priority: str = "normal",
    applicability: str = "all_agents",
) -> dict:
    combined = "\n".join((fact, why, evidence, suggested_destination))
    if contains_secret(combined):
        raise ValueError("refusing to write secret-like content to shared memory inbox")
    if applicability != "source_only" and has_ambiguous_agent_family_wording(fact, agent_names=(agent,)):
        raise ValueError(
            "ambiguous agent-family wording; use '<agent>-family agents' or set applicability=source_only"
        )

    config = load_config(root)
    inbox_dir = root / config.get("memory", {}).get("inbox_dir", "inbox") / machine / agent
    inbox_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    note_id = f"{today}-{machine}-{agent}-{safe_slug(fact)}"
    path = inbox_dir / f"{note_id}.md"
    content_hash = normalized_hash(fact)
    text = (
        "---\n"
        f"id: {note_id}\n"
        f"source_agent: {agent}\n"
        f"machine: {machine}\n"
        f"observer: {machine}/{agent}\n"
        f"date: {today}\n"
        f"type: {note_type}\n"
        f"scope: {scope}\n"
        f"applicability: {applicability}\n"
        f"priority: {priority}\n"
        "status: pending\n"
        f"content_hash: {content_hash}\n"
        "---\n\n"
        "## Source Perspective\n\n"
        f"Observed by `{machine}/{agent}`. Downstream receivers must not retell this as first-person experience unless their identity matches the observer. Applicability: `{applicability}`.\n\n"
        "## Fact\n\n"
        f"{fact}\n\n"
        "## Why It Matters\n\n"
        f"{why}\n\n"
        "## Evidence\n\n"
        f"{evidence}\n\n"
        "## Suggested Destination\n\n"
        f"{suggested_destination}\n"
    )
    path.write_text(text, encoding="utf-8")
    return {"id": note_id, "path": path, "content_hash": content_hash}
