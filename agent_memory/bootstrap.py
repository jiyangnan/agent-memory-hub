from __future__ import annotations

from pathlib import Path

from .registry import find_agent


def render_bootstrap(root: Path, *, machine: str, agent: str) -> str:
    record = find_agent(root, machine=machine, agent=agent)
    if not record:
        raise ValueError(f"agent is not registered: {machine}/{agent}")

    primary_memory = record["primary_memory"]
    return (
        "# agent memory hub Cold Start Contract\n\n"
        f"Machine: `{machine}`\n\n"
        f"Agent: `{agent}`\n\n"
        f"Primary memory: `{primary_memory}`\n\n"
        "## Rules\n\n"
        "- agent memory hub is the shared memory hub for durable cross-agent knowledge.\n"
        "- `记住这个` and `保存到记忆` mean this agent's local memory only.\n"
        "- `保存到共享记忆` and `同步给其他 agent` mean write an inbox note.\n"
        "- `拉取一下云端的记忆` and `刷新共享记忆` mean refresh cloud memory into this agent.\n"
        "- Write shared-memory proposals only under this inbox path: "
        f"`inbox/{machine}/{agent}/`.\n"
        "- Do not directly edit canonical `memory/*.md` files during normal work.\n"
        "- Never sync secrets, auth files, cookies, SQLite databases, sessions, raw logs, or runtime config.\n"
        "- Startup may refresh shared memory, but must not auto-curate by default.\n"
    )

