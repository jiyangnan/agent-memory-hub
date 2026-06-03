# Cloud Handoff

The v0.1 cloud backend is Git.

```bash
agent-memory cloud-status
agent-memory cloud-pull
agent-memory cloud-save --message "Update shared memory"
agent-memory cloud-push
```

Safety rules:

- `cloud-save` stages only shared-state paths.
- Product code edits are not included by `cloud-save`.
- Dirty worktrees block pull and push.
- Pull uses fast-forward only.
- Divergence requires manual resolution.

