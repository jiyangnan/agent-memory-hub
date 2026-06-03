# Refresh

`agent-memory refresh` is the downstream path for prompts such as:

```text
拉取一下云端的记忆
同步一下共享记忆
refresh shared memory
```

It performs two steps:

```text
cloud-pull -> managed sync
```

The pull must succeed before local agent memory is touched.

## Preview Refresh

```bash
agent-memory refresh \
  --machine laptop \
  --agent codex
```

This runs a fast-forward pull and then performs a sync dry-run.

## Apply Refresh

```bash
agent-memory refresh \
  --machine laptop \
  --agent codex \
  --apply
```

This runs a fast-forward pull and then applies the managed-section sync.

## Blocked States

Refresh returns `pull_blocked` when the repository is not a Git repository, has no remote, has local dirty state, or cannot fast-forward.

Refresh returns `sync_blocked` when the agent target is missing, outside the adapter allowlist, or has no managed marker.

Agents should report these states to the user instead of silently editing local memory.
