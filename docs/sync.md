# Managed Sync

`agent-memory sync` writes canonical shared memory into one registered agent's native memory file.

The command only edits the content between these markers:

```text
<!-- agent-memory-hub:BEGIN shared -->
<!-- agent-memory-hub:END shared -->
```

Everything outside the marker is treated as the agent's local memory and is preserved.

## Install Marker

Run this once per agent after registration:

```bash
agent-memory sync \
  --machine laptop \
  --agent codex \
  --install-marker
```

This creates a backup under `.curator/backups/` before modifying an existing target file.

## Preview

```bash
agent-memory sync \
  --machine laptop \
  --agent codex \
  --dry-run
```

Dry-run returns a JSON preview and does not modify the target memory file.

## Apply

```bash
agent-memory sync \
  --machine laptop \
  --agent codex \
  --apply
```

Apply replaces only the managed section and records local sync state under `.curator/local-sync/`.

## Safety

- The agent must be registered in `registry/agents.json`.
- The target path must stay inside the adapter allowlist.
- Missing markers block sync until `--install-marker` is run.
- Missing targets block apply and dry-run.
