# Adapters

Adapters describe how `agent memory hub` writes canonical shared memory into an agent's native memory file.

Adapter manifests live in:

```text
adapters/
```

Each adapter declares:

- primary memory path
- write mode
- managed marker
- allowlist
- cold-start installation mode
- skill target template
- safety rules

Adapters must never sync whole runtime directories.

## Built-In Adapters

- `codex`: `~/.codex/memory/shared.md`
- `claude`: `~/.claude/memory/shared.md`
- `openclaw`: `~/.openclaw/workspace/MEMORY.md`
- `hermes`: `~/.hermes/memories/MEMORY.md`

Users can override `primary_memory` at registration time.
